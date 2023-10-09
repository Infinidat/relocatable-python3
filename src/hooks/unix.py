
def chmod_configure(options, buildout, environ):
    from os import stat, chmod
    from stat import S_IEXEC

    CONFIGURE_FILENAME = './configure'
    cur_mode = stat(CONFIGURE_FILENAME).st_mode
    chmod(CONFIGURE_FILENAME, cur_mode | S_IEXEC)

def chmod_install(options, buildout, environ):
    from os import stat, chmod
    from stat import S_IEXEC

    INSTALL_PATH = 'support/install.sh'
    mode = stat(INSTALL_PATH).st_mode
    chmod(INSTALL_PATH, mode | S_IEXEC)
