__import__("pkg_resources").declare_namespace(__name__)

import os, subprocess

def _execute(cmd, env):
    process = subprocess.Popen(cmd.split(), env=env)
    return process.wait()

def openssl_pre_make(options, buildout, environ):
    _execute(r'ms\do_ms.bat', environ)

def openssl_pre_make64(options, buildout, environ):
    _execute(r'ms\do_win64a.bat', environ)

def _db_post_make(platform_name, prefix):
    import os
    os.system('cp -fvr build_windows/*h %s/include' % prefix)
    os.system('cp -fvr build_windows/%s/Release/*lib %s/lib' % (platform_name, prefix))
    os.system('cp -fvr build_windows/%s/Release/*exe %s/bin' % (platform_name, prefix))

def db_post_make(options, buildout, environ):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    _db_post_make('Win32', prefix)

def db_post_make64(options, buildout, environ):
    prefix = environ['PREFIX'].replace(os.path.sep, '/')
    _db_post_make('x64', prefix)

class PythonPostMake(object):
    def __init__(self, environ, x64_build=False):
        from os import path, curdir
        self.python_source_path = path.abspath(path.join(curdir, path.pardir))
        self.pcbuild_path = path.join(self.python_source_path, 'PCbuild')
        self.x64_build = x64_build
        if self.x64_build:
            self.pcbuild_path = path.join(self.python_source_path, 'PCbuild',
                                         'x64')
        self.prefix = environ['PREFIX']

    def make_install(self):
        self.make_pyd()
        self.make_exe()
        self.make_dll()
        self.make_lib()
        self.make_ico()
        self.make_includes()
        self.make_binaries()

    def make_pyd(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.pyd')):
            shtil.copy(pyd_file, path.join(self.prefix, 'lib'))

    def make_exe(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.exe')):
            shtil.copy(pyd_file, path.join(self.prefix, 'bin'))

    def make_dll(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.dll')):
            shtil.copy(pyd_file, path.join(self.prefix, 'lib'))

    def make_lib(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.lib')):
            shtil.copy(pyd_file, path.join(self.prefix, 'lib'))

    def make_ico(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.python_source_path,
                                            'PC', '*.ico')):
            shtil.copy(pyd_file, path.join(self.prefix, 'lib'))

    def make_includes(self):
        import shutil
        from os import path
        shutil.copytree(path.join(self.python_source_path, 'Include'),
                        self.prefix)
        shtutil.copy(path.join(self.python_source_path, 'PC', 'pyconfig.h'),
                     path.join(self.prefix, 'Include'))

    def make_binaries(self):
        import shutil
        from os import path
        shutil.copytree(path.join(self.python_source_path, 'Lib'),
                        path.join(self.prefix, 'lib', 'python2.7'))

def python_post_make(options, buildout, environ):
    instance = PythonPostMake(environ, False)
    instance.make_install()

def python_post_make64(options, buildout, environ):
    instance = PythonPostMake(environ, True)
    instance.make_install()

