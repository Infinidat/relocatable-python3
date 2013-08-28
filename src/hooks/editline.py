from infi.execute import execute_assert_success
import os


def replace_readline_with_editline(options, buildout, environ):
    if os.name == "nt":
        return
    command = "find . -type f -exec perl -p -i -e s/-lreadline/-ledit/g {} ;"
    execute_assert_success(command.split())
