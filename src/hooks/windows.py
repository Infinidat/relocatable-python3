from __future__ import print_function
import os
import posixpath
import subprocess
from os import path
import glob
import shutil

def _convert(text):
    return text.replace(os.path.sep, posixpath.sep)

def _system(cmd):
    cmd = _convert(cmd)
    print('==>', cmd)
    os.system(cmd)

def _mkdir(path):
    _system('install -v -d "%s"' % path)

def _todo(act, src, dst):
    if isinstance(src, str):
        _system('%s "%s" "%s"' % (act, src, dst))
    elif isinstance(src, (list, tuple)):
        _mkdir(dst)
        for item in src:
            _system('%s "%s" "%s"' % (act, item, dst))
    else:
        raise Exception('Unexpected source type %s' % type(src))

def _copy(src, dst):
    _todo('cp -f -r -v', src, dst)

def _move(src, dst):
    _todo('mv -f -v', src, dst)

def xz_post_make(options, buildout, environ):
    prefix = environ['PREFIX']
    suffix = 'bin_x86-64'
    _copy(glob.glob(os.path.join('include', '*.h')),
          os.path.join(prefix, 'include'))
    _copy(glob.glob(os.path.join('include', 'lzma', '*.h')),
          os.path.join(prefix, 'include', 'lzma'))
    _copy(glob.glob(os.path.join(suffix, '*.a')),
          os.path.join(prefix, 'lib'))
    _copy(glob.glob(os.path.join(suffix, '*.dll')),
          os.path.join(prefix, 'bin'))

def libiconv_post_make(options, buildout, environ):
    prefix = environ['PREFIX']
    suffix = os.path.join('build-VS2017', 'x64', 'Release')
    _copy(glob.glob(os.path.join('include', '*.h')),
          os.path.join(prefix, 'include'))
    _copy(glob.glob(os.path.join(suffix, '*.dll')),
          os.path.join(prefix, 'bin'))
    _copy(glob.glob(os.path.join(suffix, '*.lib')),
          os.path.join(prefix, 'lib'))
    _copy(os.path.join(suffix, 'libiconv.lib'),
          os.path.join(prefix, 'lib', 'iconv.lib'))
    _copy(glob.glob(os.path.join(suffix, '*.exe')),
          os.path.join(prefix, 'bin'))

def libevent_post_make(options, buildout, environ):
    0/0
    prefix = environ['PREFIX']

    os.system('cp -fvr *lib %s/lib' % prefix)

class PythonPostMake(object):
    def __init__(self, environ):
        self.arch = 'amd64'
        self.python_source_path = path.abspath(os.curdir)
        self.externals = path.join(self.python_source_path, 'externals')
        self.pcbuild_path = path.join(self.python_source_path, 'PCbuild', self.arch)
        self.prefix = environ['PREFIX']
        self.environ = environ
        print(self.python_source_path, self.pcbuild_path, self.prefix)

    def make_install(self):
        self.move_dlls()
        self.move_bins()
        self.move_libs()
        self.move_libffi()
        self.move_openssl()
        self.move_headers()
        self.copy_crt()

    def move_dlls(self):
        src = glob.glob(path.join(self.prefix, 'bin', '*.dll'))
        src = [dll for dll in src if 'python' not in dll]
        src += glob.glob(path.join(self.pcbuild_path, '*.dll'))
        src += glob.glob(path.join(self.prefix, 'lib', '*.pdb'))
        src += glob.glob(path.join(self.pcbuild_path, '*.pyd'))
        dst = path.join(self.prefix, 'DLLs')
        _move(src, dst)

    def move_bins(self):
        src = glob.glob(path.join(self.pcbuild_path, '*.exe'))
        src += glob.glob(path.join(self.pcbuild_path, '*.ico'))
        dst = path.join(self.prefix, 'bin')
        _move(src, dst)

    def move_libs(self):
        src = glob.glob(path.join(self.prefix, 'lib', '*.a'))
        src += glob.glob(path.join(self.prefix, 'lib', '*.lib'))
        src += glob.glob(path.join(self.pcbuild_path, '*.lib'))
        dst = path.join(self.prefix, 'libs')
        _move(src, dst)
        src = glob.glob(path.join(self.python_source_path, 'lib', '*'))
        dst = path.join(self.prefix, 'lib')
        _move(src, dst)

    def move_libffi(self):
        name = 'libffi-3.4.4'
        base = path.join(self.externals, name, self.arch)
        src = glob.glob(path.join(base, 'include', '*.h'))
        dst = path.join(self.prefix, 'include')
        _move(src, dst)
        src = glob.glob(path.join(base, '*.lib'))
        dst = path.join(self.prefix, 'libs')
        _move(src, dst)
        src = glob.glob(path.join(base, '*.dll'))
        dst = path.join(self.prefix, 'DLLs')
        _move(src, dst)

    def move_openssl(self):
        name = 'openssl-bin-1.1.1w'
        base = path.join(self.externals, name, self.arch)
        src = glob.glob(path.join(base, 'include', 'openssl', '*.h'))
        dst = path.join(self.prefix, 'include')
        _move(src, dst)
        src = glob.glob(path.join(base, '*.lib'))
        dst = path.join(self.prefix, 'libs')
        _move(src, dst)
        src = glob.glob(path.join(base, '*.dll'))
        dst = path.join(self.prefix, 'DLLs')
        _move(src, dst)

    def move_headers(self):
        src = glob.glob(path.join(self.python_source_path, 'Include', '*.h'))
        dst = path.join(self.prefix, 'include')
        _move(src, dst)
        src = path.join(self.python_source_path, 'PC', 'pyconfig.h')
        _move(src, dst)

    def copy_crt(self):
        src = glob.glob(path.join(self.environ['WindowsSdkDir'],
                                  'Redist', self.environ['XSDKVer'],
                                  'ucrt', 'DLLs', 'x64', '*.dll'))
        src += glob.glob(path.join(self.environ['VCRoot'],
                                   'Redist', 'MSVC', '14.16.27012',
                                   'x64', 'Microsoft.VC141.CRT', '*.dll'))
        dst = path.join(self.prefix, 'bin')
        _copy(src, dst)

def python_post_make(options, buildout, environ):
    instance = PythonPostMake(environ)
    instance.make_install()
