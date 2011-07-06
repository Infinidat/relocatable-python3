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
    repl = r'-install_name @rpath/\1 '
    open(filepath, 'w').write(sub(pattern, repl, content))

def remove_rpath_in_file(filepath):
    from re import sub
    print "pre-configure-hook: changing install_name in %s" % filepath
    content = open(filepath).read()
    content = content.replace(r'$rpath/$soname', r'@rpath/$soname')
    content = content.replace(r'\$rpath/\$soname', r'@rpath/\$soname')
    content = content.replace(r'\$rpath/\$soname', r'@rpath/\$soname')
    content = content.replace(r'${wl}-rpath ${wl}$libdir}', '')
    content = content.replace(r'${wl}-rpath,$libdir}', '')
    content = content.replace(r'-rpath $libdir}', '')
    open(filepath, 'w').write(content)

def change_install_name(options, buildout, version):
    from os import curdir
    from os.path import exists, sep, abspath
    for item in find_files(abspath(curdir), 'configure'):
        change_install_name_in_file(item)
        remove_rpath_in_file(item)
    for item in find_files(abspath(curdir), 'Makefile'):
        change_install_name_in_file(item)
        remove_rpath_in_file(item)
    for item in find_files(abspath(curdir), 'configure.in'):
        change_install_name_in_file(item)
        remove_rpath_in_file(item)
    for item in find_files(abspath(curdir), 'Makefile.in'):
        change_install_name_in_file(item)
        remove_rpath_in_file(item)
    for item in find_files(abspath(curdir), 'libtool'):
        change_install_name_in_file(item)
        remove_rpath_in_file(item)

def patch_ncurses(options, buildout, version):
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
    from os import curdir
    from os.path import exists, sep, abspath
    for item in find_files(abspath(curdir), 'Makefile*'):
        print 'fixing files "%s"' % item
        filepath = item
        content = open(filepath).read()
        content = content.replace('-Wl,-rpath,$(LIBRPATH)', '')
        content = content.replace('-Wl,-rpath,$(LIBPATH)', '')
        content = content.replace('-rpath $(LIBRPATH)', '')
        content = content.replace("-install_name $(INSTALLTOP)/$(LIBDIR)", "-install_name @rpath")
        open(filepath, 'w').write(content)

def patch_pdb(options, buildout, version):
    import pdb
    pdb.set_trace()

def patch_cyrus_sasl(options, buildout, version):
    change_install_name(options, buildout, version)
    from os import curdir
    from os.path import exists, sep, abspath
    for item in find_files(abspath(curdir), 'ltconfig'):
        change_install_name_in_file(item)
        remove_rpath_in_file(item)

def patch_python(options, buildout, version):
    from os.path import abspath
    change_install_name(options, buildout, version)
    for file in ['Makefile.pre.in', 'configure', 'configure.in']:
        content = open(file).read()
        print abspath('./%s' % file)
        assert len(content)
        content = content.replace(r'-install_name,$(prefix)/lib', '-install_name,@rpath')
        previous = content
        content = content.replace(r'-install_name $(DESTDIR)$(PYTHONFRAMEWORKINSTALLDIR)/Versions/$(VERSION)', '-install_name @rpath')
        content = content.replace(r'-install_name $(PYTHONFRAMEWORKINSTALLDIR)/Versions/$(VERSION)', '-install_name @rpath')
        assert '@rpath' in content
        open(file, 'w').write(content)

