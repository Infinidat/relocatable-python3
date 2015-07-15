/*! blibpath doesn't support relative paths, so we must fix LIBPATH and only then execve the original python !*/

#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define MAX_PATH (4096)         /*! using what's defined in linux/limits.h, on AIX there is no such definition !*/
#define WRAPPER_ERROR  (133)    /*! some distinctive error code.. !*/

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
        }
        else {
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

int get_executable_path(char * argv_0, char * output)
{
    char temp[MAX_PATH] = { 0 };

    if (strchr(argv_0, '/') != NULL) {
        /*! '/' can be either in the beginning for absolute path or in the middle for relative path !*/
        strcpy(temp, argv_0);
    } else {
        if (0 != get_from_path(argv_0, temp)) {
            return 1;
        }
    }
    if (NULL == realpath(temp, output)) {
        return 1;
    }
    return 0;
}

int main(int argc, char *argv[])
{
    char cur_executable_path[MAX_PATH] = { 0 };
    char python_bin_path[MAX_PATH] = { 0 };
    char python_lib_path[MAX_PATH] = { 0 };
    char * last_sep = NULL;
    if (0 != get_executable_path(argv[0], cur_executable_path)) {
        return WRAPPER_ERROR;
    }
    last_sep = strrchr(cur_executable_path, '/');
    if (last_sep == NULL) {
        return WRAPPER_ERROR;
    }
    *last_sep = 0;      /*! make cur_executable_path hold dirname only !*/
    sprintf(python_bin_path, "%s/python3.4.bin", cur_executable_path);
    sprintf(python_lib_path, "%s/../lib", cur_executable_path);
    setenv("LIBPATH", python_lib_path, TRUE);
    execve(python_bin_path, argv, environ);
    return WRAPPER_ERROR;
}
