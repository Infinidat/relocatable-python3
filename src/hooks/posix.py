TRICK = """
# isolated-python trick
import sys
prefix = sys.real_prefix if hasattr(sys, 'real_prefix') else sys.prefix  # virtualenv
old_prefix = build_time_vars.get("prefix", "_some_path_that_does_not_exist")

for key, value in build_time_vars.items():
    build_time_vars[key] = value.replace(old_prefix, prefix) if isinstance(value, str) else value
"""


def find_files(directory, pattern):
    import os
    import fnmatch
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def get_sysconfigdata_files(environ):
    from glob import glob
    from os import path
    dist = path.join(environ.get("PWD"), path.abspath(path.join('.',  # Python-3.x
                                                                path.pardir,  # python__compile__,
                                                                path.pardir,  # parts,
                                                                path.pardir,  # python-build
                                                                "dist")))
    print("dist = {0}".format(dist))
    print("sysconfig = {0!r}".format(glob(path.join(dist, "*", "*", "_sysconfigdata.py"))))
    for _sysconfigdata in glob(path.join(dist, "*", "*", "_sysconfigdata.py")):
        yield _sysconfigdata


def purge_sysconfigdata(path):
    with open(path, 'a') as fd:
        fd.write(TRICK)


def fix_linker_rpath(path):
    # we want to link against the .so files in python/lib, but $ORIGIN may point to
    # python/lib/python3.x/site-packages/<package-root>/<package-src>
    # (e.g. python/lib/python3.x/site-packages/lxml-3.4.1-py3.x-linux-i686.egg/lxml)
    # so we add $ORIGIN/../../../.. to rpath in linker options
    src_str = r"-Wl,-rpath,\\$ORIGIN/../.."
    dst_str = r"-Wl,-rpath,\\$ORIGIN/../..,-rpath,\\$ORIGIN/../../../.."
    with open(path, 'r') as fd:
        data = fd.read()
    data = data.replace(src_str, dst_str)
    with open(path, 'w') as fd:
        fd.write(data)


def fix_sysconfigdata(options, buildout, environ):
    for path in get_sysconfigdata_files(environ):
        purge_sysconfigdata(path)
        fix_linker_rpath(path)


def link_python_binary(options, buildout, environ):
    from os import system
    system("ln -s ./python3 {0}/bin/python".format(options["prefix"]))


def fix_lib64_libdir(options, buildout, environ):
    from os import curdir
    from os.path import abspath
    from itertools import chain
    files = chain(*[find_files(abspath(curdir), filename) for filename in ['configure', 'Makefile', 'Makefile.am', 'configure.in', 'Makefile.in']])
    for item in files:
        print('fixing file "%s"' % item)
        content = open(item).read()
        content = content.replace("$(prefix)/lib", "$(prefix)/lib64")
        open(item, 'w').write(content)


def check_relocatability(options, buildout, environ):
    from os.path import abspath
    from subprocess import check_output
    print('\n====RELOCATABILITY CHECK====\n')
    try:
        for item in find_files(abspath(options["prefix"]), '*.so*'):
            objdump_output = check_output(["objdump -x {} | grep PATH || true".format(item)], shell=True)
            ldd_output = check_output(["ldd {} | grep usr || true".format(item)], shell=True)
            if ldd_output:
                print("{} : ldd: {}".format(item, ldd_output))
            if objdump_output and '$ORIGIN' not in objdump_output:
                print("{} : objdump: {}".format(item, objdump_output))
    except:
        pass

def python_post_make(options, buildout, environ):
    fix_sysconfigdata(options, buildout, environ)
    link_python_binary(options, buildout, environ)
    check_relocatability(options, buildout, environ)
