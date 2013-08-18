def purge_sysconfigdata(options, buildout, environ):
    from glob import glob
    from os import path, curdir
    dist = path.join(environ.get("PWD"), "dist")
    [_sysconfigdata] = glob(path.join(dist, "*", "*", "_sysconfigdata.py"))
    with open(_sysconfigdata, 'w') as fd:
        fd.write("# isolated-python\nbuild_time_vars = dict()\n")
