import glob
import logging
import shutil
import stat
import os

LOG = logging.getLogger(__name__)

def onerror(function, path, excinfo):
    error = excinfo[1]
    LOG.info('%s %s: %s', function.__name__, path, error)
    if not isinstance(error, PermissionError):
        raise error
    LOG.info('chmod: %s', path)
    os.chmod(path, stat.S_IWRITE)
    function(path)

def python_pre_make(options, buildout, env):
    dist = options.get('dist')
    if os.path.exists(dist):
        LOG.info('remove %s', dist)
        shutil.rmtree(dist, onerror=onerror)

def python_post_make(options, buildout, env):
    dist = options.get('dist')
    prefix = options.get('prefix')
    sdk_dir = env.get('WindowsSdkDir')
    sdk_ver = env.get('XSDKVer')
    crt_dir = env.get('VCRoot')
    crt_ver = env.get('XCrtVer')
    if not os.path.exists(dist):
        os.makedirs(dist)
    for base, _, names in os.walk(dist):
        for name in names:
            if name.endswith('.pdb') or name.endswith('static.lib'):
                path = os.path.join(base, name)
                LOG.info('remove %s', path)
                os.remove(path)
    pairs = (
        (
            os.path.join(dist, '*.dll'),
            os.path.join(dist, 'bin')
        ),
        (
            os.path.join(dist, '*.exe'),
            os.path.join(dist, 'bin')
        ),
        (
            os.path.join(dist, 'DLLs', '*.dll'),
            os.path.join(dist, 'bin')
        )
    )
    for src, dst in pairs:
        if not os.path.exists(dst):
            LOG.info('mkdir %s', dst)
            os.makedirs(dst)
        for origin in glob.glob(src):
            name = os.path.basename(origin)
            target = os.path.join(dst, name)
            if os.path.exists(target):
                LOG.info('remove %s', target)
                if os.path.isdir(target):
                    shutil.rmtree(target, onerror=onerror)
                else:
                    os.unlink(target)
            LOG.info('move %s => %s', origin, target)
            shutil.move(origin, target)
    pairs = (
        (
            os.path.join(prefix, 'bin', '*.dll'),
            os.path.join(dist, 'bin')
        ),
        (
            os.path.join(prefix, 'lib', '*.dll'),
            os.path.join(dist, 'bin')
        ),
        (
            os.path.join(prefix, 'lib', '*.lib'),
            os.path.join(dist, 'libs')
        ),
        (
            os.path.join(prefix, 'include', '*'),
            os.path.join(dist, 'include')
        ),
        (
            os.path.join(sdk_dir, 'Redist', sdk_ver, 'ucrt', 'DLLs', 'x64', '*.dll'),
            os.path.join(dist, 'bin')
        ),
        (
            os.path.join(crt_dir, 'Redist', 'MSVC', crt_ver, 'x64', 'Microsoft.VC141.CRT', '*.dll'),
            os.path.join(dist, 'bin')
        )
    )
    for src, dst in pairs:
        if not os.path.exists(dst):
            LOG.info('mkdir %s', dst)
            os.makedirs(dst)
        for origin in glob.glob(src):
            name = os.path.basename(origin)
            target = os.path.join(dst, name)
            if os.path.isdir(origin):
                LOG.info('copy tree %s => %s', origin, target)
                shutil.copytree(origin, target)
            else:
                LOG.info('copy file %s => %s', origin, target)
                shutil.copy(origin, target)
    pairs = (
        ('zlib.lib', 'z.lib'),
    )
    for dst, src in pairs:
        origin = os.path.join(dist, 'libs', src)
        target = os.path.join(dist, 'libs', dst)
        LOG.info('copy file %s => %s', origin, target)
        shutil.copy(origin, target)
