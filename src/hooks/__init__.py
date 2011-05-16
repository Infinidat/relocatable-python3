__import__("pkg_resources").declare_namespace(__name__)

from sys import argv
from subprocess import Popen, PIPE
from platform import system

def _catch_and_print(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except (OSError, IOError), e:
        print e

def find_files(directory, pattern):
    import os, fnmatch
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)

                yield filename

def change_install_name_in_file(filepath):
    from re import sub
    print "pre-configure-hook: changing install_name in %s" % filepath
    content = open(filepath).read()
    pattern = r'-install_name .*/(.*) '
    repl = r'-install_name @rpath/\1'
    open(filepath, 'w').write(sub(pattern, repl, content))

def change_install_name(options, buildout, version):
    from os import curdir
    from os.path import exists, sep, abspath
    for item in find_files(abspath(curdir), 'config*'):
        change_install_name_in_file(item)
    for item in find_files(abspath(curdir), 'Makefile*'):
        change_install_name_in_file(item)

def patch_ncurses(options, buildout, version):
    change_install_name(options, buildout, version)
    from os import curdir
    from os.path import exists, sep, abspath
    for item in find_files(abspath(curdir), 'Makefile'):
        print 'fixing files "%s"' % item
        filepath = item
        content = open(filepath).read()
        src = 'LIBRARIES\t=  ../lib/libncurses.dylib'
        dst = 'LIBRARIES\t=  ../lib/libncurses.${ABI_VERSION}.dylib'
        open(filepath, 'w').write(content.replace(src,dst).replace('-o$@', '-o $@'))

def patch_openssl(options, buildout, version):
    change_install_name(options, buildout, version)
    from os import curdir
    from os.path import exists, sep, abspath
    for item in find_files(abspath(curdir), 'Makefile*'):
        print 'fixing files "%s"' % item
        filepath = item
        content = open(filepath).read()
        content = content.replace('-Wl,-rpath,$(LIBRPATH)', '')
        content = content.replace('-Wl,-rpath,$(LIBPATH)', '')
        content = content.replace('-rpath $(LIBRPATH)', '')
        open(filepath, 'w').write(content)

def patch_pdb(options, buildout, version):
    import pdb
    pdb.set_trace()

