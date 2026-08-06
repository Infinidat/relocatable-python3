import glob
import logging
import platform
import os
import shutil
import sys
import subprocess

LOG = logging.getLogger(__name__)

PREFIX = '__PREFIX__'
PYTHON = 'python'

MAJOR = 3
MINOR = 11

CMAKE = [
    ['cmake', '--build', 'build', '--config', 'Release'],
    ['cmake', '--install', 'build', '--config', 'Release'],
    ['ctest', '--test-dir', 'build', '--build-config', 'Release']
]

LIBTOOL = 'libtool'
AUTOGEN = 'autogen.sh'
AUTORECONF = ['autoreconf', '--force', '--install', '--verbose']

TRICK = """
import sys

PREFIX = '__PREFIX__'

for key, value in build_time_vars.items():
    if isinstance(value, str) and PREFIX in value:
        build_time_vars[key] = value.replace(PREFIX, sys.base_prefix)
"""

def run(args, env, verbose=True):
    command = ' '.join(str(arg) for arg in args)
    LOG.info('run command: %s', command)
    try:
        process = subprocess.Popen(args=args,
                                   env=env,
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
        lines = stdout.splitlines()
        for line in lines:
            LOG.info('stdout: %s', line)
    if stderr:
        lines = stderr.splitlines()
        for line in lines:
            LOG.info('stderr: %s', line)
    if status:
        message = 'command %s failed with error %d' % (command, status)
        LOG.error(message)
        raise RuntimeError(message)
    return stdout

def cmake(options, buildout, env):
    for args in CMAKE:
        run(args, env)

def libiconv(options, buildout, env):
    prefix = env.get('PREFIX')
    suffix = os.path.join('build-VS2017', 'x64', 'Release')
    pairs = (
        (
            os.path.join(suffix, 'libiconv.dll'),
            os.path.join(prefix, 'bin')
        ),
        (
            os.path.join(suffix, 'libiconv.lib'),
            os.path.join(prefix, 'lib')
        ),
        (
            os.path.join('include', 'iconv.h'),
            os.path.join(prefix, 'include')
        )
    )
    for src, dst in pairs:
        if not os.path.exists(dst):
            LOG.info('mkdir %s', dst)
            os.makedirs(dst)
        LOG.info('copy %s => %s', src, dst)
        shutil.copy(src, dst)

def libffi(options, buildout, env):
    prefix = env.get('PREFIX')
    src = os.path.join(prefix, 'lib', 'libffi.dll')
    dst = os.path.join(prefix, 'bin', 'libffi.dll')
    LOG.info('move %s => %s', src, dst)
    shutil.move(src, dst)

def autogen(options, buildout, env):
    shell = env.get('SHELL')
    args = [shell, '-exu', AUTOGEN]
    run(args, env)

def autoreconf(options, buildout, env):
    run(AUTORECONF, env)

def pre_make_hook(options, buildout, env):
    shell = env.get('SHELL')
    LOG.info('fix %s scripts for %s %s',
             LIBTOOL,
             options.get('name'),
             options.get('version'))
    cmd = r's|^(hardcode_libdir_flag_spec)=.*$|\1=""|g'
    args = [
        'find', '.', '-type', 'f', '-name', LIBTOOL, '-print',
        '-exec', 'sed', '-E', '-i', cmd, '{}', ';'
    ]
    run(args, env)
    LOG.info('fix shell scripts for %s %s',
             options.get('name'),
             options.get('version'))
    cmd = r'1s|^(#!).*sh$|\1%s|' % shell
    args = [
        'find', '.', '-type', 'f', '-name', '*.sh', '-print',
        '-exec', 'sed', '-E', '-i', cmd, '{}', ';'
    ]
    run(args, env)

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

def create_python_wrapper(options, buildout, env):
    target = platform.system().lower()
    compiler = env.get('CC')
    pflags = env.get('CPPFLAGS')
    cflags = env.get('CFLAGS')
    lflags = env.get('LDFLAGS')
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
    run(cmd, env)

def change_python_sysconfigdata(options, buildout, env):
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

def create_python_symlink(options, buildout, env):
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

def python_post_make(options, buildout, env):
    create_python_wrapper(options, buildout, env)
    change_python_sysconfigdata(options, buildout, env)
    create_python_symlink(options, buildout, env)

def create_ncurses_fallbacks(options, buildout, env):
    terminals = options.get('terminals', 'xterm')
    toolkit = options.get('toolkit', os.path.sep)
    tic = os.path.join(toolkit, 'bin', 'tic')
    infocmp = os.path.join(toolkit, 'bin', 'infocmp')
    terminfo = os.path.join(toolkit, 'share', 'terminfo')
    src = os.path.join('misc', 'terminfo.src')
    cmd = ['ncurses/tinfo/MKfallback.sh', terminfo, src, tic, infocmp]
    cmd += terminals.split(',')
    data = run(cmd, env, verbose=False)
    path = os.path.join('ncurses', 'fallback.c')
    with open(path, 'w') as file:
        file.write(data)
