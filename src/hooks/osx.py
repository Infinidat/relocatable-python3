from __future__ import print_function
__import__("pkg_resources").declare_namespace(__name__)

def _catch_and_print(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except (OSError, IOError) as e:
        print(e)

def find_files(directory, pattern):
    import os
    import fnmatch
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def change_install_name_in_file(filepath):
    from re import sub
    print("pre-configure-hook: changing install_name in %s" % filepath)
    content = open(filepath).read()
    pattern = r'-install_name .*/(.*) '
    repl = r'-install_name @rpath/\1 '
    open(filepath, 'w').write(sub(pattern, repl, content))

def remove_rpath_in_file(filepath):
    print("pre-configure-hook: changing install_name in %s" % filepath)
    content = open(filepath).read()
    content = content.replace(r'$rpath/$soname', r'@rpath/$soname')
    content = content.replace(r'\$rpath/\$soname', r'@rpath/\$soname')
    content = content.replace(r'\$rpath/\$soname', r'@rpath/\$soname')
    content = content.replace(r'${wl}-rpath ${wl}$libdir', '')
    content = content.replace(r'${wl}-rpath,$libdir', '')
    content = content.replace(r'-rpath $libdir', '')
    open(filepath, 'w').write(content)

def change_install_name(options, buildout, version, additional_files=[]):
    from os import curdir
    from os.path import abspath
    files_to_search = [
        'configure',
        'Makefile',
        'configure.in',
        'Makefile.in',
        'libtool',
        'aclocal.m4',
    ]
    files_to_search.extend(additional_files)
    for file in files_to_search:
        for item in find_files(abspath(curdir), file):
            change_install_name_in_file(item)
            remove_rpath_in_file(item)

def patch_ncurses(options, buildout, version):
    from os import curdir
    from os.path import abspath
    for item in find_files(abspath(curdir), 'Makefile'):
        print('fixing files "%s"' % item)
        filepath = item
        content = open(filepath).read()
        src = 'LIBRARIES\t=  ../lib/libncurses.dylib'
        dst = 'LIBRARIES\t=  ../lib/libncurses.${ABI_VERSION}.dylib'
        open(filepath, 'w').write(content.replace(src, dst).replace('-o$@', '-o $@'))

def patch_openssl(options, buildout, version):
    from os import curdir
    from os.path import abspath
    for item in find_files(abspath(curdir), 'shared-info*'):
        print('fixing files "%s"' % item)
        filepath = item
        content = open(filepath).read()
        content = content.replace("-install_name $(INSTALLTOP)/$(LIBDIR)", "-install_name @rpath")
        open(filepath, 'w').write(content)

def patch_pdb(options, buildout, version):
    import pdb
    pdb.set_trace()

def patch_cyrus_sasl(options, buildout, version):
    change_install_name(options, buildout, version, ['ltconfig'])

def patch_readline(options, buildout, version):
    change_install_name(options, buildout, version, ['shobj-conf'])

def patch_python(options, buildout, version):
    from os.path import abspath
    change_install_name(options, buildout, version)
    for file in ['Makefile.pre.in', 'configure']:
        content = open(file).read()
        print(abspath('./%s' % file))
        assert len(content)
        content = content.replace(r'-install_name,$(prefix)/lib', '-install_name,@rpath')
        content = content.replace(r'-install_name $(DESTDIR)$(PYTHONFRAMEWORKINSTALLDIR)/Versions/$(VERSION)', '-install_name @rpath')
        content = content.replace(r'-install_name $(PYTHONFRAMEWORKINSTALLDIR)/Versions/$(VERSION)', '-install_name @rpath')
        assert '@rpath' in content
        open(file, 'w').write(content)

def add_ld_library_path_to_python_makefile(options, buildout, version):
    # Inject LD_LIBRARY_PATH to setup.py's runtime (see comment in add_ld_library_path_to_configure)
    # without this, the dynamic modules will fail to load and be renamed to *_failed.so
    from os.path import join
    dist = options["prefix"]
    dist_lib = join(dist, "lib")
    filename = "Makefile"
    content = open(filename).read()
    content = content.replace('$(PYTHON_FOR_BUILD) $(srcdir)/setup.py', 'LD_LIBRARY_PATH={} $(PYTHON_FOR_BUILD) $(srcdir)/setup.py'.format(dist_lib))
    open(filename, 'w').write(content)

def patch_python_Makefile_after_configure(options, buildout, version):
    import re
    filename = "Makefile"
    content = open(filename).read()
    content = re.sub(r"LDFLAGS=", r"LDFLAGS=-Wl,-rpath,@loader_path/../lib ", content)
    open(filename, 'w').write(content)
    add_ld_library_path_to_python_makefile(options, buildout, version)


def patch_libevent_configure_in(options, buildout, version):
    from os import curdir
    from os.path import abspath
    for item in find_files(abspath(curdir), 'configure.in*'):
        print('fixing files "%s"' % item)
        filepath = item
        content = open(filepath).read()
        content = content.replace('AM_CONFIG_HEADER', 'AC_CONFIG_HEADERS')
        open(filepath, 'w').write(content)

def add_ld_library_path_to_configure(options, buildout, version):
    # The LD_LIBRARY_PATH (runtime search path) that is set by buildout is not passed to
    # the childrent processes due to SIP on El Capitan and newer. We set it manually inside the configure script
    from os import curdir
    from os.path import abspath, join
    filepath = join(abspath(curdir), 'configure')
    print('fixing files "%s"' % filepath)
    content = open(filepath).read()
    dist = options["prefix"]
    dist_lib = join(dist, "lib")
    content = "export LD_LIBRARY_PATH={}\n".format(dist_lib) + content
    open(filepath, 'w').write(content)

def autogen(options, buildout, version):
    from subprocess import Popen
    patch_libevent_configure_in(options, buildout, version)
    process = Popen(['./autogen.sh'])
    assert process.wait() == 0
    change_install_name(options, buildout, version)

def autoreconf(options, buildout, version):
    from subprocess import Popen
    patch_libevent_configure_in(options, buildout, version)
    process = Popen(['autoreconf'])
    assert process.wait() == 0
    change_install_name(options, buildout, version)
