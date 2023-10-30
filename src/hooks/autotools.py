import os

AUTOTOOLS = [
#    'libtoolize --copy',
#    'aclocal -I m4 --install',
#    'autoheader',
#    'autoconf',
#    'automake --foreign --add-missing --force-missing --copy'
    'autoreconf --force --install'
]

def autogen(options, buildout, version):
    rc = 0
    for cmd in AUTOTOOLS:
        rc += os.system(cmd)
    if rc != 0:
        raise Exception('autotools error: %d' % rc)

def libtool(options, buildout, version):
    cmd = "sed -i.orig -e 's|-lstdc++||g' -e 's|-lsupc++||g' libtool"
    rc = os.system(cmd)
    if rc != 0:
        raise Exception('libtool error: %d' % rc)
