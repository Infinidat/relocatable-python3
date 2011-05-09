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

