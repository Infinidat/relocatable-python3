TRICK = """
# isolated-python trick
import sys
prefix = sys.real_prefix if hasattr(sys, 'real_prefix') else sys.prefix  # virtualenv
old_prefix = build_time_vars.get("prefix", "_some_path_that_does_not_exist")

for key, value in build_time_vars.items():
    build_time_vars[key] = value.replace(old_prefix, prefix) if isinstance(value, str) else value
"""

def purge_sysconfigdata(options, buildout, environ):
    from glob import glob
    from os import path, curdir
    dist = path.join(environ.get("PWD"), path.abspath(path.join('.',  # Python-2.7.6
                                                                path.pardir,  # python__compile__,
                                                                path.pardir,  # parts,
                                                                path.pardir,  # python-build
                                                                "dist")))
    print 'dist = {0}'.format(dist)
    print 'sysconfig = {0!r}'.format(glob(path.join(dist, "*", "*", "_sysconfigdata.py")))
    [_sysconfigdata] = glob(path.join(dist, "*", "*", "_sysconfigdata.py"))
    with open(_sysconfigdata, 'a') as fd:
        fd.write(TRICK)
