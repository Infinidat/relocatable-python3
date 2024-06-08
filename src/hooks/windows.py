from __future__ import print_function
import os
import subprocess
from os import path
import glob
import shutil

def _execute(cmd, env):
    process = subprocess.Popen(cmd.split(), env=env)
    return process.wait()

def _xz_post_make(environ, platform):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    os.system('cp -fvr include/* %s/include' % prefix)
    os.system('cp -fvr bin_%s/*a %s/lib' % (platform, prefix))
    os.system('cp -fvr bin_%s/*dll %s/bin' % (platform, prefix))

def xz_post_make(options, buildout, environ):
    _xz_post_make(environ, "x86-64")

def _libiconv_post_make(platform_name, prefix):
    import os
    os.system('cp -fvr include/*h %s/include' % prefix)
    os.system('cp -fvr build-VS2017/%s/Release/*lib %s/lib' % (platform_name, prefix))
    os.system('cp -fvr build-VS2017/%s/Release/*dll %s/lib' % (platform_name, prefix))
    os.system('cp -fvr build-VS2017/%s/Release/*exe %s/bin' % (platform_name, prefix))
    os.system('cp -fvr %s/lib/libiconv.lib %s/lib/iconv.lib' % (prefix, prefix))

def libiconv_post_make(options, buildout, environ):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    _libiconv_post_make('x64', prefix)

def _libffi_post_make(platform_name, prefix):
    import os
    # libffi-python runs from Python source
    python_source_path = path.abspath(path.join(os.curdir, path.pardir)).replace(os.path.sep, '/')
    os.system('cp -fvr %s/externals/libffi/%s/include/*.h %s/include' % (python_source_path, platform_name, prefix))
    os.system('cp -fvr %s/externals/libffi/%s/*.lib %s/lib' % (python_source_path, platform_name, prefix))
    os.system('cp -fvr %s/externals/libffi/%s/*.dll %s/lib' % (python_source_path, platform_name, prefix))

def libffi_post_make(options, buildout, environ):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    _libffi_post_make('amd64', prefix)

def tcl_post_make(options, buildout, environ):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    os.system('chmod -R 744 %s/lib/tcl8.6/tzdata' % prefix)
    os.system('chmod -R 744 %s/lib/tcl8.6/msgs' % prefix)

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
        items = glob.glob(path.join(self.prefix, 'bin', '*.dll'))
        items += glob.glob(path.join(self.prefix, 'lib', '*.pdb'))
        items += glob.glob(path.join(self.pcbuild_path, '*.pyd'))
        dst = path.join(self.prefix, 'DLLs')
        mkdir(dst)
        for item in items:
            if 'python311.dll' in item:
                continue
            _system('mv -fv %s %s' % (item, dst))

    def move_bins(self):
        items = glob.glob(path.join(self.pcbuild_path, '*.dll'))
        items += glob.glob(path.join(self.pcbuild_path, '*.exe'))
        items += glob.glob(path.join(self.pcbuild_path, '*.ico'))
        dst = path.join(self.prefix, 'bin')
        mkdir(dst)
        for item in items:
            _system('mv -fv %s %s' % (item, dst))

    def move_libs(self):
        items = glob.glob(path.join(self.prefix, 'lib', '*.a'))
        items += glob.glob(path.join(self.prefix, 'lib', '*.lib'))
        items += glob.glob(path.join(self.pcbuild_path, '*.lib'))
        dst = path.join(self.prefix, 'libs')
        mkdir(dst)
        for item in items:
            _system('mv -fv %s %s' % (item, dst))
        items = glob.glob(path.join(self.python_source_path, 'lib', '*'))
        dst = path.join(self.prefix, 'lib')
        mkdir(dst)
        for item in items:
            _system('mv -fv %s %s' % (item, dst))

    def move_libffi(self):
        name = 'libffi-3.4.4'
        base = path.join(self.externals, name, self.arch)
        _system('mv -fv %s %s' % (path.join(base, 'include', '*'),
                                  path.join(self.prefix, 'include')))
        _system('mv -fv %s %s' % (path.join(base, '*.lib'),
                                  path.join(self.prefix, 'libs')))
        _system('mv -fv %s %s' % (path.join(base, '*.dll'),
                                  path.join(self.prefix, 'DLLs')))

    def move_openssl(self):
        name = 'openssl-bin-1.1.1w'
        base = path.join(self.externals, name, self.arch)
        _system('mv -fv %s %s' % (path.join(base, 'include', '*'),
                                  path.join(self.prefix, 'include')))
        _system('mv -fv %s %s' % (path.join(base, '*.lib'),
                                  path.join(self.prefix, 'libs')))
        _system('mv -fv %s %s' % (path.join(base, '*.dll'),
                                  path.join(self.prefix, 'DLLs')))

    def move_headers(self):
        _system('mv -fv %s %s' % (path.join(self.python_source_path, 'Include', '*'),
                                  path.join(self.prefix, 'include')))
        _system('mv -fv %s %s' % (path.join(self.python_source_path, 'PC', 'pyconfig.h'),
                                  path.join(self.prefix, 'include')))

    def copy_crt(self):
        items = glob.glob(path.join(self.environ['WindowsSdkDir'],
                                    'Redist', self.environ['XSDKVer'],
                                    'ucrt', 'DLLs', 'x64', '*.dll'))
        items += glob.glob(path.join(self.environ['VCRoot'],
                                     'Redist', 'MSVC', '14.16.27012',
                                     'x64', 'Microsoft.VC141.CRT', '*.dll'))
        dst = path.join(self.prefix, 'bin')
        mkdir(dst)
        for item in items:
            _system('cp -fv %s %s' % (item, dst))

def mkdir(path):
    if os.path.exists(path):
        return
    os.makedirs(path)

def _system(cmd):
    cmd = cmd.replace(os.path.sep, '/')
    print(cmd)
    os.system(cmd)

def libevent_post_make(options, buildout, environ):
    import os
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    os.system('cp -fvr *lib %s/lib' % prefix)

def python_post_make(options, buildout, environ):
    instance = PythonPostMake(environ)
    instance.make_install()
