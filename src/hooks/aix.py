import os
import sys
import subprocess

TRICK = """
import sys

PREFIX = '__PREFIX__'

if prefix != PREFIX:
    for key, value in build_time_vars.items():
        if isinstance(value, str) and PREFIX in value:
            build_time_vars[key] = value.replace(PREFIX, sys.prefix)
"""

def run(args):
    process = subprocess.Popen(args=args,
                               close_fds=True,
                               universal_newlines=True,
                               stdout=subprocess.stdout,
                               stderr=subprocess.stderr)
    stdout, stderr = process.communicate()
    stdout = stdout.splitlines()
    stderr = stderr.splitlines()
    if process.returncode:
        command = ' '.join(str(arg) for arg in args)
        error = ' '.join(stdout.splitlines + stderr.splitlines)
        raise Exception(error)

def get_python_name(prefix=False, major=False, minor=False, binary=False):
    name = 'python'
    if prefix:
        name = os.path.join(prefix, name)
    if major:
        name += str(sys.version_info.major)
        if minor:
            name += '.' + str(sys.version_info.minor)
            if binary:
                name += '.bin'
    return name

def change_python_maxdata(options, buildout, environ):
    prefix = options.get('prefix')
    path = get_python_name(prefix=prefix, major=True, minor=True)
    cmd = ['ldedit', '-b', 'maxdata:0x20000000', path]
    run(cmd)

def create_python_wrapper(options, buildout, environ):
    compile = environ.get('CC')
    prefix = options.get('prefix')
    hooks = options.get('hooks-dir')
    src = get_python_name(prefix=prefix, major=True, minor=True)
    dst = get_python_name(prefix=prefix, major=True, minor=True, binary=True)
    cmd = '%s -s %s/aix.c -o %s' % (compile, hooks, src)
    os.rename(src, dst)
    run(cmd)

def get_python_sysconfigdata():
    abi = sys.abiflags
    platform = sys.platform
    multiarch = getattr(sys.implementation, '_multiarch', '')
    name = '_sysconfigdata_%s_%s_%s.py' % (abi, platform, multiarch)
    dest = get_python_name(prefix='lib', major=True, minor=True)
    path = os.path.join(sys.prefix, dest, name)
    return path

def change_python_sysconfigdata(options, buildout, environ):
    prefix = options.get('prefix')
    path = get_python_sysconfigdata()
    with open(path, 'r') as fd:
        data = fd.read()
    data = data.replace(prefix, PREFIX)
    with open(path, 'w') as fd:
        fd.write(data)
        fd.write(TRICK)

def change_python_headers(options, buildout, environ):
    # _LARGE_FILES definition causes redefinition errors in external library compilation
    prefix = options.get('prefix')
    dest = get_python_name(prefix='include', major=True, minor=True)
    path = os.path.join(prefix, dest, 'pyconfig.h')
    with open(path, 'r') as fd:
        data = fd.read()
    data = data.replace('#define _LARGE_FILES 1', '')
    with open(path, 'w') as fd:
        fd.write(data)

def create_python_symlink(options, buildout, environ):
    prefix = options.get('prefix')
    src = get_python_name(major=True)
    dst = get_python_name(prefix=prefix)
    os.symlink(src, dst)

def python_post_make(options, buildout, environ):
    change_python_maxdata(options, buildout, environ)
    create_python_wrapper(options, buildout, environ)
    change_python_sysconfigdata(options, buildout, environ)
    change_python_headers(options, buildout, environ)
    create_python_symlink(options, buildout, environ)
