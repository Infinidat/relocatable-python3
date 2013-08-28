from infi.execute import execute_assert_success

def replace_readline_with_editline(options, buildout, environ):
    command = "find . -type f -exec perl -p -i -e s/-lreadline/-ledit/g {} ;"
    execute_assert_success(command.split())
