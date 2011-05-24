
import os, subprocess
from os import path
import glob

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
        dst = path.join(self.prefix, 'DLLs')
        src = glob.glob(path.join(self.pcbuild_path, '*.pyd'))
        _copy_files(src, dst)

    def make_exe(self):
        dst = path.join(self.prefix, 'bin')
        src = glob.glob(path.join(self.pcbuild_path, '*.exe'))
        _copy_files(src, dst)

    def make_dll(self):
        dst = path.join(self.prefix, 'bin')
        src = glob.glob(path.join(self.pcbuild_path, '*.dll'))
        _copy_files(src, dst)

    def make_lib(self):
        dst = path.join(self.prefix, 'libs')
        src = glob.glob(path.join(self.pcbuild_path, '*.lib'))
        _copy_files(src, dst)

    def make_ico(self):
        dst = path.join(self.prefix, 'bin')
        src = glob.glob(path.join(self.pcbuild_path, '*.ico'))
        _copy_files(src, dst)

    def make_includes(self):
        import shutil
        from os import path
        cmd = "cp -fr %s %s" % (path.join(self.python_source_path, 'Include'),
                                path.join(self.prefix))
        _system(cmd)
        shutil.copy(path.join(self.python_source_path, 'PC', 'pyconfig.h'),
                     path.join(self.prefix, 'Include'))

    def make_libraries(self):
        from os import path
        dst = path.join(self.prefix, 'lib')
        src = path.join(self.python_source_path, 'lib')
        my_path(dst)
        cmd = "cp -fr %s %s" % (src, dst)
        _system(cmd)

def _mk_path(path):
    if os.path.exists(path):
        return
    os.makedirs(path)

def _copy_files(src_glob, dst):
    _mk_path(dst)
    for item in src_glob:
        print 'cp %s %s' % (item, dst)
        shutil.copy(item, dst)

def _system(cmd):
    print cmd
    os.system(cmd.replace(os.path.sep, '/'))

def python_post_make(options, buildout, environ):
    instance = PythonPostMake(environ, False)
    instance.make_install()

def python_post_make64(options, buildout, environ):
    instance = PythonPostMake(environ, True)
    instance.make_install()

if __name__ == '__main__':
    environ = {'PREFIX': r'C:\Users\jenkins\workspace\python-feature-v2.7.1-windows\label\windows-x86\dist'}
    python_post_make(None, None, environ)
