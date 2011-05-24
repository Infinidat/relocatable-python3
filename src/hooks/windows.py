
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

        print self.python_source_path, self.pcbuild_path, self.prefix

    def make_install(self):
        self.make_pyd()
        self.make_exe()
        self.make_dll()
        self.make_lib()
        self.make_ico()
        self.make_includes()
        self.make_libraries()

    def make_pyd(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.pyd')):
            print 'cp %s %s' % (pyd_file, path.join(self.prefix, 'DLLs'))
            shutil.copy(pyd_file, path.join(self.prefix, 'DLLs'))

    def make_exe(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.exe')):
            print 'cp %s %s' % (pyd_file, path.join(self.prefix, 'bin'))
            shutil.copy(pyd_file, path.join(self.prefix, 'bin'))

    def make_dll(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.dll')):
            print 'cp %s %s' % (pyd_file, path.join(self.prefix, 'bin'))
            shutil.copy(pyd_file, path.join(self.prefix, 'bin'))

    def make_lib(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.pcbuild_path, '*.lib')):
            print 'cp %s %s' % (pyd_file, path.join(self.prefix, 'libs'))
            shutil.copy(pyd_file, path.join(self.prefix, 'libs'))

    def make_ico(self):
        import glob
        import shutil
        from os import path
        for pyd_file in glob.glob(path.join(self.python_source_path,
                                            'PC', '*.ico')):
            print 'cp %s %s' % (pyd_file, path.join(self.prefix, 'lib'))
            shutil.copy(pyd_file, path.join(self.prefix, 'lib'))

    def make_includes(self):
        import shutil
        from os import path
        shutil.copytree(path.join(self.python_source_path, 'Include'),
                        path.join(self.prefix, 'Include'))
        shutil.copy(path.join(self.python_source_path, 'PC', 'pyconfig.h'),
                     path.join(self.prefix, 'Include'))

    def make_libraries(self):
        import shutil
        import glob
        from os import path
        cmd = "cp -fr %s %s" % (path.join(self.python_source_path, 'lib'),
                                    path.join(self.prefix, 'lib'))
        print cmd
        os.system(cmd)

def python_post_make(options, buildout, environ):
    instance = PythonPostMake(environ, False)
    instance.make_install()

def python_post_make64(options, buildout, environ):
    instance = PythonPostMake(environ, True)
    instance.make_install()

if __name__ == '__main__':
    environ = {'PREFIX': r'C:\Users\jenkins\workspace\python-feature-v2.7.1-windows\label\windows-x86\dist'}
    python_post_make(None, None, environ)
