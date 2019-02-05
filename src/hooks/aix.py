import os

TRICK = """
# isolated-python trick
import sys
prefix = sys.real_prefix if hasattr(sys, 'real_prefix') else sys.prefix  # virtualenv
old_prefix = build_time_vars.get("prefix", "_some_path_that_does_not_exist")

for key, value in build_time_vars.items():
    value = value.replace(old_prefix, prefix) if isinstance(value, str) else value
    build_time_vars[key] = value.replace("./Modules", prefix + "/lib/python3.7/config") if isinstance(value, str) else value
"""

def find_files(directory, pattern):
    import os
    import fnmatch
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def get_sysconfigdata_files(options):
    from glob import glob
    from os import path
    dist = options["prefix"]
    print("dist = {0}".format(dist))
    print("sysconfig = {0!r}".format(glob(path.join(dist, "*", "*", "_sysconfigdata.py"))))
    for _sysconfigdata in glob(path.join(dist, "*", "*", "_sysconfigdata.py")):
        yield _sysconfigdata

def purge_sysconfigdata(path):
    with open(path, 'a') as fd:
        fd.write(TRICK)

def create_blibpath_fix(options, buildout, environ):
    os.system("mv {0}/bin/python3.7 {0}/bin/python3.7.bin".format(options["prefix"]))
    os.system("gcc -s {}/aix.c -o {}/bin/python3.7".format(options["hooks-dir"], options["prefix"]))

def fix_sysconfigdata(options, buildout, environ):
    for path in get_sysconfigdata_files(options):
        purge_sysconfigdata(path)

def fix_large_files(options, buildout, environ):
    # _LARGE_FILES definition causes redefinition errors in external library compilation
    dist = options["prefix"]
    pyconfig_path = os.path.join(dist, "include", "python3.7m", "pyconfig.h")
    with open(pyconfig_path, "r") as fd:
        data = fd.read()
    data = data.replace("#define _LARGE_FILES 1", "")
    with open(pyconfig_path, "w") as fd:
        fd.write(data)

def fix_max_memory(options, buildout, environ):
    # allow 512MB memory allocation for the process. See README.AIX in Python's code
    os.system("ldedit -b maxdata:0x20000000 {0}/bin/python3.7".format(options["prefix"]))

def link_python_binary(options, buildout, environ):
    os.system("ln -s ./python3 {0}/bin/python".format(options["prefix"]))

def check_relocatability(options, buildout, environ):
    from os.path import abspath
    from subprocess import check_output
    print('\n====RELOCATABILITY CHECK====\n')
    try:
        for item in find_files(abspath(options["prefix"]), '*.so*'):
            dump_output = check_output(['dump -H {} | grep "^0 " || true'.format(item)], shell=True)
            if dump_output and '$ORIGIN' not in dump_output:
                print("{} : dump: {}".format(item, dump_output))
    except:
        pass

def python_post_make(options, buildout, environ):
    fix_max_memory(options, buildout, environ)
    create_blibpath_fix(options, buildout, environ)
    fix_sysconfigdata(options, buildout, environ)
    fix_large_files(options, buildout, environ)
    link_python_binary(options, buildout, environ)
    check_relocatability(options, buildout, environ)