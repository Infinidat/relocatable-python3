__import__("pkg_resources").declare_namespace(__name__)

from sys import argv
from subprocess import Popen
from platform import system

def build(argv = argv):
    command = './bin/buildout -c buildout-build.cfg'
    if system() == 'Darwin':
        command = './bin/buildout -c buildout-build-osx.cfg'
    process = Popen(command.split())
    stdout, stderr = process.communicate()
    exit(process.returncode)

def pack(argv = argv):
    command = './bin/buildout -c buildout-pack.cfg'
    process = Popen(command.split())
    stdout, stderr = process.communicate()
    exit(process.returncode)

def clean(argv = argv):
    from os.path import abspath, curdir, sep, pardir
    from os import mkdir
    from glob import glob
    from shutil import rmtree, move

    base = abspath(sep.join([__file__, pardir, pardir, pardir]))
    dist = sep.join([base, 'dist'])
    parts = sep.join([base, 'parts'])

    print "base = %s" % repr(base)

    print "rm -rf %s" % repr(dist)
    _catch_and_print(rmtree, *[dist])

    src = sep.join([parts, 'buildout'])
    dst = sep.join([base ,'buildout'])
    print "mv %s %s" % (repr(src), repr(dst))
    _catch_and_print(move, *[src, dst])

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

