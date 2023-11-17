import os

AUTOGEN = './autogen.sh_'

AUTOTOOLS = [
#    'libtoolize --copy',
#    'aclocal -I m4 --install',
#    'autoheader',
#    'autoconf',
#    'automake --foreign --add-missing --force-missing --copy'
    'autoreconf --force --install --verbose'
]

def autogen(options, buildout, version):
    rc = 0
    cmds = AUTOTOOLS
    if os.path.exists(AUTOGEN):
        cmds = [AUTOGEN]
    for cmd in cmds:
        rc += os.system(cmd)
    if rc != 0:
        raise Exception('autotools %s error: %d' % (cmd, rc))

def libtool(options, buildout, version):
    cmd = "sed -i.orig -e 's|-lstdc++||g' -e 's|-lsupc++||g' libtool"
    rc = os.system(cmd)
    if rc != 0:
        raise Exception('libtool %s error: %d' % (cmd, rc))
