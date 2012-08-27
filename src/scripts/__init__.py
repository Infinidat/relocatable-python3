__import__("pkg_resources").declare_namespace(__name__)

from sys import argv
from subprocess import Popen
from platform import system
from sys import exit

def build(argv = ' '.join(argv[1:])):
    command = './bin/buildout -c buildout-build.cfg %s' % argv
    if system() == 'Linux':
        from platform import dist
        dist_name = dist()[0].lower()
        if dist_name == 'ubuntu':
            command = './bin/buildout -c buildout-build-ubuntu.cfg %s' % argv
        if dist_name in ['redhat', 'centos']:
            command = './bin/buildout -c buildout-build-redhat-64bit.cfg %s' % argv
    elif system() == 'Darwin':
        command = './bin/buildout -c buildout-build-osx.cfg %s' % argv
    elif system() == 'Windows':
        from sys import maxsize
        if maxsize > 2**32:
            command = './bin/buildout -c buildout-build-windows-64bit.cfg %s' % argv
        else:
            command = './bin/buildout -c buildout-build-windows.cfg %s' % argv
    print 'executing "%s"' % command
    process = Popen(command.split())
    stdout, stderr = process.communicate()
    exit(process.returncode)

def pack(argv = ' '.join(argv[1:])):
    command = './bin/buildout -c buildout-pack.cfg %s' % argv
    if system() == 'Windows':
        command = './bin/buildout -c buildout-pack-windows.cfg %s' % argv
    print 'executing "%s"' % command
    process = Popen(command.split())
    stdout, stderr = process.communicate()
    exit(process.returncode)

def clean(argv = ' '.join(argv[1:])):
    from os.path import abspath, curdir, pardir, exists
    from os import mkdir, remove, path
    from glob import glob
    from shutil import rmtree, move

    sep = '/'
    filepath = __file__.replace(path.sep, '/')
    base = abspath(sep.join([filepath, pardir, pardir, pardir]))
    dist = sep.join([base, 'dist'])
    parts = sep.join([base, 'parts'])
    installed_file = sep.join([base, '.installed-build.cfg'])

    print "base = %s" % repr(base)

    for tar_gz in glob(sep.join([base, '*tar.gz'])):
        print "rm %s" % tar_gz
        remove(tar_gz)

    print "rm -rf %s" % repr(dist)
    _catch_and_print(rmtree, *[dist])

    src = sep.join([parts, 'buildout'])
    dst = sep.join([base ,'buildout'])

    print "mv %s %s" % (repr(src), repr(dst))
    _catch_and_print(move, *[src, dst])

    print "rm %s" % repr(installed_file)
    if exists(installed_file):
        remove(installed_file)

    print "rm -rf %s" % repr(parts)
    _catch_and_print(rmtree, *[parts])

    print "mkdir %s" % repr(parts)
    _catch_and_print(mkdir, *[parts])

    dst = sep.join([parts, 'buildout'])
    src = sep.join([base ,'buildout'])
    print "mv %s %s" % (repr(src), repr(dst))
    _catch_and_print(move, *[src, dst])

def _catch_and_print(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except (OSError, IOError), e:
        print e

