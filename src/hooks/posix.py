from __future__ import print_function

TRICK = """
# isolated-python trick
import sys
prefix = sys.real_prefix if hasattr(sys, 'real_prefix') else sys.prefix  # virtualenv
old_prefix = build_time_vars.get("prefix", "_some_path_that_does_not_exist")

for key, value in build_time_vars.items():
    build_time_vars[key] = value.replace(old_prefix, prefix) if isinstance(value, str) else value
"""

def get_sysconfigdata_files(environ):
    from glob import glob
    from os import path
    dist = path.join(environ.get("PWD"), path.abspath(path.join('.',  # Python-3.8.0
                                                                path.pardir,  # python__compile__,
                                                                path.pardir,  # parts,
                                                                path.pardir,  # python-build
                                                                "dist")))
    print('dist = {0}'.format(dist))
    print('sysconfig = {0!r}'.format(glob(path.join(dist, "*", "*", "_sysconfigdata.py"))))
    for _sysconfigdata in glob(path.join(dist, "*", "*", "_sysconfigdata.py")):
        yield _sysconfigdata


def purge_sysconfigdata(path):
    with open(path, 'a') as fd:
        fd.write(TRICK)


def fix_linker_rpath(path):
    # we want to link against the .so files in python/lib, but $ORIGIN may point to
    # python/lib/python3.8/site-packages/<package-root>/<package-src>
    # (e.g. python/lib/python3.8/site-packages/lxml-3.4.1-py3.8-linux-i686.egg/lxml)
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


def python_post_make(options, buildout, environ):
    fix_sysconfigdata(options, buildout, environ)
    link_python_binary(options, buildout, environ)

def make_ncurses_fallbacks(options, buildout, environ):
    from os import system, curdir
    from os.path import abspath
    system(
        "{0}/ncurses/tinfo/MKfallback.sh /lib/terminfo {0}/ncurses/misc/terminfo.src"
        " `which tic` `which infocmp` linux vt100 xterm xterm-256color >{0}/ncurses/fallback.c"
        .format(abspath(curdir)))
