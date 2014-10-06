
def chmod_configure(options, buildout, environ):
    from os import stat, chmod
    from stat import S_IEXEC

    CONFIGURE_FILENAME = './configure'
    cur_mode = stat(CONFIGURE_FILENAME).st_mode
    chmod(CONFIGURE_FILENAME, cur_mode | S_IEXEC)
