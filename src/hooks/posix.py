import glob
import logging
import platform
import os
import sys
import subprocess

LOG = logging.getLogger(__name__)

PREFIX = '__PREFIX__'
PYTHON = 'python'

MAJOR = 3
MINOR = 11

LIBTOOL = 'libtool'
AUTORECONF = ['autoreconf', '--force', '--install', '--verbose']

TRICK = """
import sys

PREFIX = '__PREFIX__'

for key, value in build_time_vars.items():
    if isinstance(value, str) and PREFIX in value:
        build_time_vars[key] = value.replace(PREFIX, sys.base_prefix)
"""

def create_python_logger(options, buildout, environ):
    LOG.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    fmt = '[%(filename)s:%(lineno)s:%(funcName)s] %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    LOG.addHandler(handler)

def run(args, verbose=True):
    command = ' '.join(str(arg) for arg in args)
    LOG.info('run command: %s', command)
    try:
        process = subprocess.Popen(args=args,
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except Exception as error:
        message = 'failed to run command %s: %s' % (command, error)
        LOG.error(message)
        raise RuntimeError(message)
    stdout, stderr = process.communicate()
    status = process.returncode
    if verbose and stdout:
        LOG.info(stdout)
    if stderr:
        LOG.error(stderr)
    if status:
        message = 'command %s failed with error %d' % (command, status)
        LOG.error(message)
        raise RuntimeError(message)
    return stdout

def autogen(options, buildout, environ):
    run(AUTORECONF)

def pre_make_hook(options, buildout, environ):
    LOG.info('fix GNU libtool for %s %s',
             options.get('name'),
             options.get('version'))
    args = ['find', '.', '-type', 'f', '-name', LIBTOOL,
            '-exec', 'sed', '-E', '-i.orig',
            's|^(hardcode_libdir_flag_spec)=.*$|\\1=""|g',
            '{}', ';']
    run(args)

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

def create_python_wrapper(options, buildout, environ):
    target = platform.system().lower()
    compiler = environ.get('CC')
    pflags = environ.get('CPPFLAGS')
    cflags = environ.get('CFLAGS')
    lflags = environ.get('LDFLAGS')
    prefix = options.get('prefix')
    hooks = options.get('hooks-dir')
    hook = target + '.c'
    hook = os.path.join(hooks, hook)
    suffix = 'bin'
    if not os.path.exists(hook):
        LOG.info('skip wrapper creation for target %s', target)
        return
    src = get_python_name(prefix=prefix, suffix=suffix, major=True, minor=True)
    dst = get_python_name(prefix=prefix, suffix=suffix, major=True, minor=True, ext=suffix)
    cmd = compiler.split() + pflags.split() + cflags.split() + lflags.split()
    cmd += ['-s', hook, '-o', src]
    LOG.info('rename %s => %s', src, dst)
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
        with open(path, 'r') as file:
            data = file.read()
        data = data.replace(prefix, PREFIX)
        with open(path, 'w') as file:
            file.write(data)
            file.write(TRICK)

def create_python_symlink(options, buildout, environ):
    prefix = options.get('prefix')
    suffix = 'bin'
    src = get_python_name(major=True)
    dst = get_python_name(prefix=prefix, suffix=suffix)
    if os.path.exists(dst):
        if not os.path.islink(dst):
            message = 'path %s is not a symlink' % dst
            LOG.error(message)
            raise RuntimeError(message)
        LOG.info('unlink existing symlink %s', dst)
        os.unlink(dst)
    LOG.info('create symlink %s => %s', dst, src)
    os.symlink(src, dst)

def python_post_make(options, buildout, environ):
    create_python_wrapper(options, buildout, environ)
    change_python_sysconfigdata(options, buildout, environ)
    create_python_symlink(options, buildout, environ)

def create_ncurses_fallbacks(options, buildout, environ):
    terminals = options.get('terminals', 'xterm')
    toolkit = options.get('toolkit', os.path.sep)
    tic = os.path.join(toolkit, 'bin', 'tic')
    infocmp = os.path.join(toolkit, 'bin', 'infocmp')
    terminfo = os.path.join(toolkit, 'share', 'terminfo')
    src = os.path.join('misc', 'terminfo.src')
    cmd = ['ncurses/tinfo/MKfallback.sh', terminfo, src, tic, infocmp]
    cmd += terminals.split(',')
    data = run(cmd, verbose=False)
    path = os.path.join('ncurses', 'fallback.c')
    with open(path, 'w') as file:
        file.write(data)
