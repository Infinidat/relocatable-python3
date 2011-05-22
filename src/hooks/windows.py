__import__("pkg_resources").declare_namespace(__name__)

import os, subprocess

def _execute(cmd, env):
    process = subprocess.Popen(cmd.split(), env=env)
    return process.wait()

def openssl_pre_make(options, buildout, environ):
    _execute(r'ms\do_ms.bat', environ)

def openssl_pre_make64(options, buildout, environ):
    _execute(r'ms\do_win64a', environ)

