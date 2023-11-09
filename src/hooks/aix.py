import glob
import logging
import os
import sys
import subprocess

LOG = logging.getLogger(__name__)

PREFIX = '__PREFIX__'
PYTHON = 'python'
MAJOR = 3
MINOR = 8

TRICK = """
import sys

PREFIX = '__PREFIX__'

for key, value in build_time_vars.items():
    if isinstance(value, str) and PREFIX in value:
        build_time_vars[key] = value.replace(PREFIX, sys.prefix)
"""

def create_python_logger(options, buildout, environ):
    LOG.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    fmt = '[%(filename)s:%(lineno)s:%(funcName)s] %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    LOG.addHandler(handler)

def run(args):
    LOG.debug(args)
    command = ' '.join(str(arg) for arg in args)
    try:
        process = subprocess.Popen(args=args,
                                   close_fds=True,
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except Exception as error:
        message = 'Error running %s: %s' % (command, error)
        LOG.exception(message)
    stdout, stderr = process.communicate()
    stdout = stdout.splitlines()
    stderr = stderr.splitlines()
    status = process.returncode
    if status:
        output = ' '.join(stdout + stderr)
        message = 'Error %d running %s: %s' % (status, command, output)
        LOG.exception(message)

def get_python_name(prefix=None, suffix=None, major=False, minor=False, ext=None):
    name = PYTHON
    if suffix is not None:
        name = os.path.join(suffix, name)
    if prefix is not None:
        name = os.path.join(prefix, name)
    if major:
        name += str(MAJOR)
        if minor:
            name += '.' + str(MINOR)
            if ext is not None:
                name += '.' + ext
    return name

def change_python_maxdata(options, buildout, environ):
    prefix = options.get('prefix')
    suffix = 'bin'
    name = get_python_name(prefix=prefix, suffix=suffix, major=True, minor=True)
    cmd = ['ldedit', '-b', 'maxdata:0x20000000', name]
    run(cmd)

def create_python_wrapper(options, buildout, environ):
    compiler = environ.get('CC')
    prefix = options.get('prefix')
    hooks = options.get('hooks-dir')
    hook = os.path.join(hooks, 'aix.c')
    suffix = 'bin'
    src = get_python_name(prefix=prefix, suffix=suffix, major=True, minor=True)
    dst = get_python_name(prefix=prefix, suffix=suffix, major=True, minor=True, ext=suffix)
    cmd = compiler.split()
    opt = ['-s', hook, '-o', src]
    cmd.extend(opt)
    LOG.debug('rename %s => %s', src, dst)
    os.rename(src, dst)
    run(cmd)

def change_python_sysconfigdata(options, buildout, environ):
    prefix = options.get('prefix')
    suffix = 'lib'
    name = get_python_name(prefix=prefix, suffix=suffix, major=True, minor=True)
    pattern = '_sysconfigdata_*.py'
    pattern = os.path.join(name, pattern)
    paths = glob.glob(pattern)
    for path in paths:
        with open(path, 'r') as fd:
            data = fd.read()
        data = data.replace(prefix, PREFIX)
        with open(path, 'w') as fd:
            fd.write(data)
            fd.write(TRICK)

def change_python_headers(options, buildout, environ):
    # _LARGE_FILES definition causes redefinition errors in external library compilation
    prefix = options.get('prefix')
    suffix = 'include'
    name = get_python_name(prefix=prefix, suffix=suffix, major=True, minor=True)
    path = os.path.join(name, 'pyconfig.h')
    with open(path, 'r') as fd:
        data = fd.read()
    data = data.replace('#define _LARGE_FILES 1', '')
    with open(path, 'w') as fd:
        fd.write(data)

def create_python_symlink(options, buildout, environ):
    prefix = options.get('prefix')
    suffix = 'bin'
    src = get_python_name(major=True)
    dst = get_python_name(prefix=prefix, suffix=suffix)
    if os.path.exists(dst):
        if not os.path.islink(dst):
            message = 'file %s is not a symlink' % dst
            LOG.exception(message)
        LOG.debug('unlink existing symlink %s', dst)
        os.unlink(dst)
    LOG.debug('create symlink %s => %s', dst, src)
    os.symlink(src, dst)

def python_post_make(options, buildout, environ):
    create_python_logger(options, buildout, environ)
    change_python_maxdata(options, buildout, environ)
    create_python_wrapper(options, buildout, environ)
    change_python_sysconfigdata(options, buildout, environ)
    # change_python_headers(options, buildout, environ)
    create_python_symlink(options, buildout, environ)
