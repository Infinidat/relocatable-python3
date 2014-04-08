def make(options, buildout, version):
    from subprocess import Popen
    from os import name
    if name == 'nt':
        return
    process = Popen(['make'])
    process.wait()
