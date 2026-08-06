#!/usr/bin/env python3
"""Verify versions and dynamic-library provenance of a Python distribution.

Despite the historical filename, this script supports both Windows and
Unix systems.  Unix verification uses ``ldd`` and is intended for Linux,
Solaris, and AIX.

The script must be run by the Python interpreter from the distribution that
is being checked.  Each external component is enabled by passing its
``--*-library`` option; omitted components are skipped.  For every enabled
component it verifies both:

* the runtime versions reported by Python or by the native libraries;
* that each native dependency is dynamically loaded from this distribution.
"""

from __future__ import annotations

import argparse
import ctypes
import fnmatch
import importlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


class VerificationError(RuntimeError):
    """A distribution verification failed."""


def normalize_version(value: str) -> str:
    """Return the numeric/version-suffix part of a version string."""
    value = value.strip()
    match = re.search(r"\d+(?:\.\d+)+(?:[A-Za-z][A-Za-z0-9]*)?", value)
    return match.group(0).lower() if match else value.lower()


def versions_match(actual: str, expected: str) -> bool:
    actual_normalized = normalize_version(actual)
    expected_normalized = normalize_version(expected)
    return (
        actual_normalized == expected_normalized
        or actual_normalized.startswith(expected_normalized + ".")
        or expected_normalized.startswith(actual_normalized + ".")
    )


def check_version(label: str, actual: str, expected: str) -> None:
    if not versions_match(actual, expected):
        raise VerificationError(
            f"{label}: expected {expected!r}, got {actual!r}"
        )
    print(f"[OK] {label}: {actual}")


def is_below(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
    except ValueError:
        return False
    return True


def import_module(name: str):
    try:
        return importlib.import_module(name)
    except Exception as error:
        raise VerificationError(f"cannot import {name}: {error}") from error


def module_binary(module) -> Path:
    filename = getattr(module, "__file__", None)
    if filename:
        return Path(filename)
    return Path(sys.executable)


def call_c_string(path: Path, symbol: str) -> str:
    try:
        library = ctypes.CDLL(str(path))
        function = getattr(library, symbol)
        function.argtypes = []
        function.restype = ctypes.c_char_p
        value = function()
    except Exception as error:
        raise VerificationError(
            f"cannot call {symbol} from {path}: {error}"
        ) from error

    if not value:
        raise VerificationError(f"{symbol} from {path} returned NULL")
    return value.decode("ascii", "replace")


def split_patterns(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def name_matches(name: str, patterns: str) -> bool:
    if os.name == "nt":
        name = name.lower()
        return any(fnmatch.fnmatch(name, item.lower()) for item in split_patterns(patterns))
    return any(fnmatch.fnmatch(name, item) for item in split_patterns(patterns))


def find_distribution_library(
    label: str,
    library_dir: Path,
    patterns: str,
) -> Path:
    """Find a shared library directly in the distribution library directory."""
    for entry in sorted(library_dir.iterdir(), key=lambda path: path.name):
        if not entry.is_file() or not name_matches(entry.name, patterns):
            continue
        resolved = entry.resolve()
        if not is_below(resolved, library_dir):
            raise VerificationError(
                f"{label}: {entry} resolves to {resolved}, "
                f"not below {library_dir}"
            )
        print(f"[OK] {label} shared library: {resolved}")
        return resolved

    raise VerificationError(
        f"{label}: no library matching {patterns!r} in {library_dir}"
    )


class WindowsDependencies:
    """Resolve already loaded DLLs using the Windows loader."""

    def __init__(self, library_dir: Path):
        self.library_dir = library_dir.resolve()
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
        self.kernel32.GetModuleHandleW.restype = ctypes.c_void_p
        self.kernel32.GetModuleFileNameW.argtypes = [
            ctypes.c_void_p,
            ctypes.c_wchar_p,
            ctypes.c_uint,
        ]
        self.kernel32.GetModuleFileNameW.restype = ctypes.c_uint

    def _loaded_path(self, name: str) -> Path | None:
        handle = self.kernel32.GetModuleHandleW(name)
        if not handle:
            return None

        size = 32768
        buffer = ctypes.create_unicode_buffer(size)
        length = self.kernel32.GetModuleFileNameW(handle, buffer, size)
        if not length:
            error = ctypes.get_last_error()
            raise VerificationError(
                f"GetModuleFileNameW({name!r}) failed with error {error}"
            )
        return Path(buffer.value).resolve()

    def resolve(self, label: str, owner, patterns: str) -> Path:
        # Importing the owner forces its native dependencies to be loaded.
        del owner

        candidates: list[str] = []
        for pattern in split_patterns(patterns):
            if not any(character in pattern for character in "*?["):
                candidates.append(pattern)
                continue
            if self.library_dir.is_dir():
                candidates.extend(
                    entry.name
                    for entry in self.library_dir.iterdir()
                    if entry.is_file() and name_matches(entry.name, pattern)
                )

        for candidate in dict.fromkeys(candidates):
            path = self._loaded_path(candidate)
            if path is None:
                continue
            if not is_below(path, self.library_dir):
                raise VerificationError(
                    f"{label}: {candidate} was loaded from {path}, "
                    f"not from {self.library_dir}"
                )
            print(f"[OK] {label} is dynamic: {path}")
            return path

        raise VerificationError(
            f"{label}: no loaded DLL matching {patterns!r}; "
            "the dependency may be static or missing"
        )


class UnixDependencies:
    """Resolve native dependencies by inspecting an owner binary with ldd."""

    def __init__(self, library_dir: Path, linker_tool: str | None):
        self.library_dir = library_dir.resolve()
        self.tool = linker_tool or shutil.which("ldd")
        if not self.tool:
            raise VerificationError(
                "ldd was not found; specify it explicitly with --linker-tool"
            )
        self.cache: dict[Path, str] = {}

    def _output(self, binary: Path) -> str:
        binary = binary.resolve()
        if binary in self.cache:
            return self.cache[binary]
        try:
            process = subprocess.run(
                [self.tool, str(binary)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
        except OSError as error:
            raise VerificationError(
                f"cannot execute {self.tool} for {binary}: {error}"
            ) from error
        if process.returncode != 0:
            raise VerificationError(
                f"{self.tool} failed for {binary} with exit code "
                f"{process.returncode}:\n{process.stdout}"
            )
        self.cache[binary] = process.stdout
        return process.stdout

    @staticmethod
    def _path_from_line(line: str) -> Path | None:
        # Linux/Solaris: libfoo.so => /prefix/lib/libfoo.so (0x...)
        match = re.search(r"=>\s+(\S+)", line)
        if match:
            token = match.group(1)
            if token == "not":
                return None
        else:
            fields = line.strip().split()
            if not fields:
                return None
            token = fields[0]

        # AIX may print /prefix/lib/libfoo.a(member.o).
        archive = re.match(r"^(.*\.a)\([^)]*\)$", token)
        if archive:
            token = archive.group(1)

        if not os.path.isabs(token):
            return None
        return Path(token)

    def resolve(self, label: str, owner, patterns: str) -> Path:
        binary = module_binary(owner)
        output = self._output(binary)

        matched_unresolved = False
        for line in output.splitlines():
            fields = line.strip().split()
            names = [os.path.basename(field) for field in fields[:3]]
            if not any(name_matches(name, patterns) for name in names):
                continue
            if "not found" in line:
                matched_unresolved = True
                continue
            path = self._path_from_line(line)
            if path is None or not name_matches(path.name, patterns):
                continue
            resolved = path.resolve()
            if not is_below(resolved, self.library_dir):
                raise VerificationError(
                    f"{label}: {resolved} is used by {binary}, "
                    f"not a library from {self.library_dir}"
                )
            print(f"[OK] {label} is dynamic: {resolved} (used by {binary})")
            return resolved

        if matched_unresolved:
            detail = "the dependency is present but unresolved"
        else:
            detail = "the dependency may be static or missing"
        raise VerificationError(
            f"{label}: {self.tool} found no resolved library matching "
            f"{patterns!r} for {binary}; {detail}\n{output}"
        )


def tcl_library_version(path: Path) -> str:
    try:
        library = ctypes.CDLL(str(path))
        function = library.Tcl_GetVersion
        function.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        function.restype = None
        major = ctypes.c_int()
        minor = ctypes.c_int()
        patch = ctypes.c_int()
        release_type = ctypes.c_int()
        function(
            ctypes.byref(major),
            ctypes.byref(minor),
            ctypes.byref(patch),
            ctypes.byref(release_type),
        )
    except Exception as error:
        raise VerificationError(
            f"cannot call Tcl_GetVersion from {path}: {error}"
        ) from error
    return f"{major.value}.{minor.value}.{patch.value}"


def version_from_metadata(dist: Path, package: str) -> str | None:
    """Read an exact Tcl/Tk patch level without initializing a GUI."""
    variables = {
        "tcl": ("TCL_PATCH_LEVEL", "Tcl"),
        "tk": ("TK_PATCH_LEVEL", "Tk"),
    }
    variable, tcl_package = variables[package]

    for filename in dist.rglob("*Config.sh"):
        try:
            text = filename.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = re.search(
            rf"(?m)^{re.escape(variable)}=['\"]?([^'\"\s]+)", text
        )
        if match:
            return match.group(1)

    for filename in dist.rglob("pkgIndex.tcl"):
        try:
            text = filename.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = re.search(
            rf"package\s+ifneeded\s+{re.escape(tcl_package)}\s+([0-9.]+)",
            text,
        )
        if match:
            return match.group(1)
    return None


def add_library_argument(
    parser: argparse.ArgumentParser,
    option: str,
    help_text: str,
) -> None:
    parser.add_argument(
        option,
        dest=option[2:].replace("-", "_"),
        metavar="NAME_OR_PATTERN",
        help=help_text,
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify external-library versions and dynamic provenance for a "
            "Windows, Linux, Solaris, or AIX Python distribution."
        )
    )
    parser.add_argument("--dist", required=True, type=Path)
    parser.add_argument(
        "--library-dir",
        type=Path,
        help="runtime library directory (default: DIST/bin on Windows, DIST/lib on Unix)",
    )
    parser.add_argument(
        "--linker-tool",
        help="Unix ldd executable; ignored on Windows",
    )

    for option, label in (
        ("python", "Python"),
        ("openssl", "OpenSSL"),
        ("zlib", "zlib"),
        ("sqlite", "SQLite"),
        ("libffi", "libffi"),
        ("bzip2", "bzip2"),
        ("liblzma", "liblzma"),
        ("tcl", "Tcl"),
        ("tk", "Tk"),
        ("expat", "Expat"),
    ):
        if option == "python":
            help_text = "expected Python version"
        else:
            help_text = (
                f"expected {label} version; required when the corresponding "
                "library option is specified"
            )
        parser.add_argument(
            f"--{option}-version",
            required=option == "python",
            metavar="VERSION",
            help=help_text,
        )

    add_library_argument(
        parser,
        "--openssl-ssl-library",
        "SSL library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--openssl-crypto-library",
        "crypto library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--zlib-library",
        "zlib library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--sqlite-library",
        "SQLite library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--libffi-library",
        "libffi library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--bzip2-library",
        "bzip2 library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--liblzma-library",
        "liblzma library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--tcl-library",
        "Tcl library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--tk-library",
        "Tk library name or comma-separated patterns",
    )
    add_library_argument(
        parser,
        "--expat-library",
        "Expat library name or comma-separated patterns",
    )
    args = parser.parse_args(argv)

    requirements = (
        (
            "openssl_ssl_library",
            "openssl_version",
            "--openssl-ssl-library",
            "--openssl-version",
        ),
        (
            "openssl_crypto_library",
            "openssl_version",
            "--openssl-crypto-library",
            "--openssl-version",
        ),
        ("zlib_library", "zlib_version", "--zlib-library", "--zlib-version"),
        ("sqlite_library", "sqlite_version", "--sqlite-library", "--sqlite-version"),
        ("libffi_library", "libffi_version", "--libffi-library", "--libffi-version"),
        ("bzip2_library", "bzip2_version", "--bzip2-library", "--bzip2-version"),
        (
            "liblzma_library",
            "liblzma_version",
            "--liblzma-library",
            "--liblzma-version",
        ),
        ("tcl_library", "tcl_version", "--tcl-library", "--tcl-version"),
        ("tk_library", "tk_version", "--tk-library", "--tk-version"),
        ("expat_library", "expat_version", "--expat-library", "--expat-version"),
    )
    for library_attr, version_attr, library_option, version_option in requirements:
        if (
            getattr(args, library_attr) is not None
            and getattr(args, version_attr) is None
        ):
            parser.error(
                f"{version_option} is required when {library_option} is specified"
            )

    return args


def skip_component(label: str, option: str) -> None:
    print(f"[SKIP] {label}: {option} was not specified")


def verify(args: argparse.Namespace) -> None:
    dist = args.dist.resolve()
    if not dist.is_dir():
        raise VerificationError(f"distribution directory does not exist: {dist}")

    executable = Path(sys.executable).resolve()
    if not is_below(executable, dist):
        raise VerificationError(
            f"run this script using the distribution interpreter; "
            f"{executable} is not below {dist}"
        )
    print(f"[OK] interpreter: {executable}")
    check_version("Python", sys.version.split()[0], args.python_version)

    library_options = (
        args.openssl_ssl_library,
        args.openssl_crypto_library,
        args.zlib_library,
        args.sqlite_library,
        args.libffi_library,
        args.bzip2_library,
        args.liblzma_library,
        args.tcl_library,
        args.tk_library,
        args.expat_library,
    )
    dependencies = None
    if any(value is not None for value in library_options):
        default_library_dir = dist / ("bin" if os.name == "nt" else "lib")
        library_dir = (args.library_dir or default_library_dir).resolve()
        if not library_dir.is_dir():
            raise VerificationError(
                f"runtime library directory does not exist: {library_dir}"
            )

        if os.name == "nt":
            dependencies = WindowsDependencies(library_dir)
        elif os.name == "posix":
            dependencies = UnixDependencies(library_dir, args.linker_tool)
        else:
            raise VerificationError(f"unsupported operating system: {os.name}")

    if args.openssl_ssl_library is not None or args.openssl_crypto_library is not None:
        assert dependencies is not None
        ssl_module = import_module("_ssl")
        if args.openssl_ssl_library is not None:
            dependencies.resolve(
                "OpenSSL SSL", ssl_module, args.openssl_ssl_library
            )
        else:
            skip_component("OpenSSL SSL", "--openssl-ssl-library")
        if args.openssl_crypto_library is not None:
            dependencies.resolve(
                "OpenSSL crypto", ssl_module, args.openssl_crypto_library
            )
        else:
            skip_component("OpenSSL crypto", "--openssl-crypto-library")
        ssl_public = import_module("ssl")
        check_version("OpenSSL", ssl_public.OPENSSL_VERSION, args.openssl_version)
    else:
        skip_component("OpenSSL", "--openssl-ssl-library/--openssl-crypto-library")

    if args.zlib_library is not None:
        assert dependencies is not None
        zlib_module = import_module("zlib")
        zlib_path = dependencies.resolve("zlib", zlib_module, args.zlib_library)
        check_version(
            "zlib Python compile-time", zlib_module.ZLIB_VERSION, args.zlib_version
        )
        check_version(
            "zlib Python runtime", zlib_module.ZLIB_RUNTIME_VERSION, args.zlib_version
        )
        check_version(
            "zlib native runtime",
            call_c_string(zlib_path, "zlibVersion"),
            args.zlib_version,
        )
    else:
        skip_component("zlib", "--zlib-library")

    if args.sqlite_library is not None:
        assert dependencies is not None
        sqlite_module = import_module("sqlite3")
        sqlite_native = import_module("_sqlite3")
        sqlite_path = dependencies.resolve(
            "SQLite", sqlite_native, args.sqlite_library
        )
        check_version(
            "SQLite Python runtime", sqlite_module.sqlite_version, args.sqlite_version
        )
        check_version(
            "SQLite native runtime",
            call_c_string(sqlite_path, "sqlite3_libversion"),
            args.sqlite_version,
        )
    else:
        skip_component("SQLite", "--sqlite-library")

    if args.libffi_library is not None:
        assert dependencies is not None
        ctypes_module = import_module("_ctypes")
        libffi_path = dependencies.resolve(
            "libffi", ctypes_module, args.libffi_library
        )
        check_version(
            "libffi native runtime",
            call_c_string(libffi_path, "ffi_get_version"),
            args.libffi_version,
        )
    else:
        skip_component("libffi", "--libffi-library")

    if args.bzip2_library is not None:
        assert dependencies is not None
        bz2_module = import_module("_bz2")
        bzip2_path = dependencies.resolve(
            "bzip2", bz2_module, args.bzip2_library
        )
        check_version(
            "bzip2 native runtime",
            call_c_string(bzip2_path, "BZ2_bzlibVersion"),
            args.bzip2_version,
        )
    else:
        skip_component("bzip2", "--bzip2-library")

    if args.liblzma_library is not None:
        assert dependencies is not None
        lzma_module = import_module("_lzma")
        liblzma_path = dependencies.resolve(
            "liblzma", lzma_module, args.liblzma_library
        )
        check_version(
            "liblzma native runtime",
            call_c_string(liblzma_path, "lzma_version_string"),
            args.liblzma_version,
        )
    else:
        skip_component("liblzma", "--liblzma-library")

    if args.tcl_library is not None or args.tk_library is not None:
        assert dependencies is not None
        assert library_dir is not None

        tkinter_native = None
        tcl_interp = None
        if importlib.util.find_spec("_tkinter") is not None:
            tkinter_native = import_module("_tkinter")
            tkinter = import_module("tkinter")
            tcl_interp = tkinter.Tcl()
        elif args.tk_library is not None:
            raise VerificationError(
                "cannot verify Tk because Python has no _tkinter module"
            )

        if args.tcl_library is not None:
            if tkinter_native is not None:
                tcl_path = dependencies.resolve(
                    "Tcl", tkinter_native, args.tcl_library
                )
            else:
                tcl_path = find_distribution_library(
                    "Tcl", library_dir, args.tcl_library
                )
            check_version(
                "Tcl native runtime", tcl_library_version(tcl_path), args.tcl_version
            )
            if tcl_interp is not None:
                tcl_patchlevel = str(tcl_interp.eval("info patchlevel"))
                check_version("Tcl Python runtime", tcl_patchlevel, args.tcl_version)
            else:
                print(
                    "[SKIP] Tcl Python runtime: Python has no _tkinter module"
                )
        else:
            skip_component("Tcl", "--tcl-library")

        if args.tk_library is not None:
            assert tkinter_native is not None
            assert tcl_interp is not None
            dependencies.resolve("Tk", tkinter_native, args.tk_library)
            tk_version = version_from_metadata(dist, "tk")
            if tk_version is None:
                # This can fail when Tk cannot connect to a display.
                try:
                    tk_version = str(tcl_interp.eval("package require Tk"))
                except Exception as error:
                    raise VerificationError(
                        "cannot determine the exact Tk patch level from metadata "
                        f"and Tk initialization failed: {error}"
                    ) from error
            check_version("Tk runtime", tk_version, args.tk_version)
        else:
            skip_component("Tk", "--tk-library")
    else:
        skip_component("Tcl", "--tcl-library")
        skip_component("Tk", "--tk-library")

    if args.expat_library is not None:
        assert dependencies is not None
        pyexpat = import_module("pyexpat")
        expat_path = dependencies.resolve("Expat", pyexpat, args.expat_library)
        check_version(
            "Expat Python runtime", pyexpat.EXPAT_VERSION, args.expat_version
        )
        check_version(
            "Expat native runtime",
            call_c_string(expat_path, "XML_ExpatVersion"),
            args.expat_version,
        )
    else:
        skip_component("Expat", "--expat-library")

    print("\nSUCCESS: all versions and dynamic-library provenance checks passed")


def main(argv: Iterable[str] | None = None) -> int:
    try:
        verify(parse_args(argv))
    except VerificationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
