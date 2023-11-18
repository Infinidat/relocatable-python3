#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <libgen.h>
#include <limits.h>

/*! If you want proof that Unix is evil, here you go !*/
int get_from_path(char * name, char * output) {
    char * paths = strdup(getenv("PATH"));
    char * cur_path = paths;
    char * cur_sep = NULL;

    if (paths == NULL) {
        return 1;
    }

    do {
        cur_sep = strchr(cur_path, ':');

        if (cur_sep != NULL) {
            cur_sep[0] = 0;
        }

        /*! append name to cur_path !*/
        if (cur_path[strlen(cur_path)-1] == '/') {
            sprintf(output, "%s%s", cur_path, name);
        } else {
            sprintf(output, "%s/%s", cur_path, name);
        }

        /*! check if file exists and executable !*/
        if (access(output, X_OK) != -1) {
            free(paths);
            return 0;
        }

        cur_path = cur_sep + 1;
    } while (cur_sep != NULL);

    free(paths);

    return 1;
}

int get_run_path(char * input, char * output)
{
    char path[PATH_MAX] = { 0 };

    if (strchr(input, '/') == NULL) {
        if (get_from_path(input, path) != 0) {
            return 1;
        }
    } else {
        if (strcpy(path, input) == NULL) {
            return 1;
        }
    }

    if (realpath(path, output) == NULL) {
        return 1;
    }

    return 0;
}

int main(int argc, char *argv[])
{
    char exec_path[PATH_MAX] = { 0 };
    char term_path[PATH_MAX] = { 0 };
    char lib_path[PATH_MAX] = { 0 };
    char run_path[PATH_MAX] = { 0 };
    char *base_path = NULL;
    char *bin_path = NULL;
    int len = 0;

    if (get_run_path(argv[0], run_path) != 0) {
        return EXIT_FAILURE;
    }

    bin_path = dirname(run_path);

    if (bin_path == NULL) {
        return EXIT_FAILURE;
    }

    len = snprintf(exec_path, sizeof(exec_path),
                   "%s/python3.8.bin", bin_path);

    if (len > PATH_MAX) {
        return EXIT_FAILURE;
    }

    base_path = dirname(bin_path);

    if (base_path == NULL) {
        return EXIT_FAILURE;
    }

    len = snprintf(lib_path, sizeof(lib_path),
                   "%s/lib", base_path);

    if (len > PATH_MAX) {
        return EXIT_FAILURE;
    }

    len = snprintf(term_path, sizeof(term_path),
                   "%s/share/terminfo", base_path);

    if (len > PATH_MAX) {
        return EXIT_FAILURE;
    }

    setenv("LIBPATH", lib_path, TRUE);
    setenv("TERMINFO", term_path, TRUE);

    argv[0] = exec_path;

    if (execve(exec_path, argv, environ) == -1) {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
