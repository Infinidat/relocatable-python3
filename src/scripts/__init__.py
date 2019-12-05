from __future__ import print_function
__import__("pkg_resources").declare_namespace(__name__)
from subprocess import Popen
from platform import system
from infi.execute import execute_assert_success


def test():
    from logging import basicConfig, getLogger, DEBUG
    from subprocess import Popen
    from os import path, name
    from glob import glob
    basicConfig(level=DEBUG)
    python = path.join('dist', 'bin', 'python%s' % ('.exe' if name == 'nt' else ''))
    getLogger(__name__).info("testing %s" % python)
    test_files = glob(path.join("tests", "test_*.py"))
    for test_file in test_files:
        assert Popen([python, test_file]).wait() == 0


def execte_buildout(buildout_file, env=None):
    import sys
    argv = ' '.join(sys.argv[1:])
    command = "./bin/buildout -c {0} {1}".format(buildout_file, argv)
    print('executing "%s"' % command)
    process = Popen(command.split(), env=env)
    stdout, stderr = process.communicate()
    sys.exit(process.returncode)


def build():
    from sys import maxsize
    from os import environ
    from platform import version
    environ = environ.copy()
    buildout_file = 'buildout-build.cfg'
    if system() == 'Linux':
        from distro import linux_distribution
        dist_name, version, distid = linux_distribution(full_distribution_name=False)
        dist_name = dist_name.replace('rhel', 'redhat').replace('sles', 'suse').replace('enterpriseenterpriseserver', 'oracle')
        if dist_name == 'ubuntu':
            if version >= '16.04':
                buildout_file = 'buildout-build-ubuntu-16.04.cfg'
            else:
                buildout_file = 'buildout-build-ubuntu.cfg'
        if dist_name in ['redhat', 'centos']:
            arch = execute_assert_success(["uname", "-i"]).get_stdout().lower()
            if 'ppc64le' in arch:
                buildout_file = 'buildout-build-redhat-ppc64le.cfg'
            elif 'ppc64' in arch:
                buildout_file = 'buildout-build-redhat-ppc64.cfg'
            elif 'i386' in arch:
                buildout_file = 'buildout-build-redhat-32bit.cfg'
            elif int(version.split(".")[0]) > 6 or \
                (int(version.split(".")[0]) == 6 and int(version.split(".")[1]) >= 4):
                if version.startswith('8'):
                    buildout_file = 'buildout-build-redhat-8-64bit.cfg'
                else:
                    # arch is 64 bit and supports libvirt
                    buildout_file = 'buildout-build-redhat-64bit-with-libvirt.cfg'
            else:
                # arch is 64 bit
                buildout_file = 'buildout-build-redhat-64bit.cfg'
        if dist_name in ['suse']:
            arch = execute_assert_success(["uname", "-i"]).get_stdout().lower()
            if 'ppc64le' in arch:
                buildout_file = 'buildout-build-suse-ppc64le.cfg'
            elif 'ppc64' in arch:
                buildout_file = 'buildout-build-suse-ppc64.cfg'
            elif version >= "15":
                buildout_file = 'buildout-build-suse-15.cfg'
    elif system() == 'Darwin':
        from platform import mac_ver
        environ["MACOSX_DEPLOYMENT_TARGET"] = '.'.join(mac_ver()[0].split('.', 2)[:2])
        gcc_version = execute_assert_success(["gcc", "--version"]).get_stdout()
        if 'version 5.' in gcc_version:
            buildout_file = 'buildout-build-osx-xcode-5.cfg'
        elif 'version 6.' in gcc_version:
            buildout_file = 'buildout-build-osx-xcode-6.cfg'
        elif 'version 7.' in gcc_version:
            buildout_file = 'buildout-build-osx-xcode-7.cfg'
        elif 'version 8.' in gcc_version:
            buildout_file = 'buildout-build-osx-xcode-8.cfg'
        elif 'version 9.' in gcc_version:
            buildout_file = 'buildout-build-osx-xcode-8.cfg'
        elif 'version 10.' in gcc_version:
            buildout_file = 'buildout-build-osx-xcode-8.cfg'
        elif 'version 11.' in gcc_version:
            buildout_file = 'buildout-build-osx-xcode-8.cfg'
        else:
            buildout_file = 'buildout-build-osx.cfg'
    elif system() == 'Windows':
        if maxsize > 2**32:
            buildout_file = 'buildout-build-windows-64bit.cfg'
        else:
            buildout_file = 'buildout-build-windows.cfg'
    elif system() == "SunOS":
        if 'sparc' in execute_assert_success(["isainfo"]).get_stdout().lower():
            buildout_file = 'buildout-build-solaris-sparc.cfg'
            if '11.4' in version():
                buildout_file = 'buildout-build-solaris-11.4-sparc.cfg'
        elif '64' in execute_assert_success(["isainfo", "-b"]).get_stdout():
            buildout_file = 'buildout-build-solaris-64bit.cfg'
            if '11.4' in version():
                buildout_file = 'buildout-build-solaris-11.4-64bit.cfg'
        else:
            pass  # TODO support 32 bit
    elif system() == "AIX":
        from os import uname
        aix_version = "{0[3]}.{0[2]}".format(uname())
        if aix_version == "7.1":
            buildout_file = 'buildout-build-aix.cfg'
        elif aix_version == "7.2":
            buildout_file = 'buildout-build-aix-7.2.cfg'
    execte_buildout(buildout_file, environ)

def pack():
    buildout_file = 'buildout-pack.cfg'
    if system() == 'Windows':
        buildout_file = 'buildout-pack-windows.cfg'
    elif system() == "AIX":
        buildout_file = 'buildout-pack-aix.cfg'
    execte_buildout(buildout_file)

def clean():
    from os.path import abspath, pardir, exists
    from os import mkdir, remove, path
    from glob import glob
    from shutil import rmtree, move

    sep = '/'
    filepath = __file__.replace(path.sep, '/')
    base = abspath(sep.join([filepath, pardir, pardir, pardir]))
    dist = sep.join([base, 'dist'])
    parts = sep.join([base, 'parts'])
    installed_file = sep.join([base, '.installed-build.cfg'])

    print("base = %s" % repr(base))

    for tar_gz in glob(sep.join([base, '*tar.gz'])):
        print("rm %s" % tar_gz)
        remove(tar_gz)

    print("rm -rf %s" % repr(dist))
    _catch_and_print(rmtree, *[dist])

    src = sep.join([parts, 'buildout'])
    dst = sep.join([base, 'buildout'])

    print("mv %s %s" % (repr(src), repr(dst)))
    _catch_and_print(move, *[src, dst])

    print("rm %s" % repr(installed_file))
    if exists(installed_file):
        remove(installed_file)

    print("rm -rf %s" % repr(parts))
    _catch_and_print(rmtree, *[parts])

    print("mkdir %s" % repr(parts))
    _catch_and_print(mkdir, *[parts])

    dst = sep.join([parts, 'buildout'])
    src = sep.join([base, 'buildout'])
    print("mv %s %s" % (repr(src), repr(dst)))
    _catch_and_print(move, *[src, dst])


def _catch_and_print(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except (OSError, IOError) as e:
        print(e)

