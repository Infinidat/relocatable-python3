__import__("pkg_resources").declare_namespace(__name__)

import os

def openssl_pre_make(options, buildout, version):
    os.system(r'ms\do_ms.bat')

def openssl_pre_make64(options, buildout, version):
    os.system(r'ms\do_win64a')

