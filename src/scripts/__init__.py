import os
import sys
import stat
import shutil
import platform
import subprocess

from infi.os_info import get_platform_string

def onerror(function, path, info):
    error = info[1]
    if not isinstance(error, PermissionError):
        raise error
    os.chmod(path, stat.S_IWRITE)
    function(path)

def buildout(config):
    env = os.environ.copy()
    cmd = os.path.join('bin', 'buildout')
    args = [cmd, '-c', config]
    print('==> call', ' '.join(args))
    result = subprocess.call(args=args, env=env)
    raise SystemExit(result)

def build():
    system = platform.system()
    if system in ('AIX', 'SunOS'):
        import resource
        ulimits = (
            (resource.RLIMIT_CPU, resource.RLIM_INFINITY),
            (resource.RLIMIT_CORE, resource.RLIM_INFINITY),
            (resource.RLIMIT_DATA, resource.RLIM_INFINITY),
            (resource.RLIMIT_FSIZE, resource.RLIM_INFINITY),
            (resource.RLIMIT_NOFILE, 2 ** 14)
        )
        for limit, value in ulimits:
            resource.setrlimit(limit, (value, value))
    info = get_platform_string()
    config = 'buildout-build-%s.cfg' % info
    buildout(config)

def pack():
    system = platform.system()
    if system == 'AIX':
        config = 'buildout-pack-aix.cfg'
    elif system == 'Windows':
        config = 'buildout-pack-windows.cfg'
    else:
        config = 'buildout-pack.cfg'
    buildout(config)

def clean():
    folders = ['.cache', 'dist', 'parts']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder, onerror=onerror)
