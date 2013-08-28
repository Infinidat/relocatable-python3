from infi.execute import execute_assert_success
import os


def replace_readline_with_editline(options, buildout, environ):
    if os.name == "nt":
        return
    command = "find . -type f -exec perl -p -i -e s/-lreadline/-ledit/g {} ;"
    execute_assert_success(command.split())


def editline_preconfigure_hook(options, buildout, environ):
    env = {key: value for key, value in os.environ.iteritems()}
    env['LC_ALL'] = 'C'
    execute_assert_success(["aclocal"], env=env)
    execute_assert_success(["autoconf"], env=env)
    execute_assert_success(["automake"], env=env)
