url

URL to the package that will be downloaded and extracted. The supported package formats are .tar.gz, .tar.bz2, and .zip. The value must be a full URL, e.g. http://python.org/ftp/python/2.4.4/Python-2.4.4.tgz. The path option can not be used at the same time with url.

path

Path to a local directory containing the source code to be built and installed. The directory must contain the configure script. The url option can not be used at the same time with path.

prefix

Custom installation prefix passed to the --prefix option of the configure script. Defaults to the location of the part. Note that this is a convenience shortcut which assumes that the default configure command is used to configure the package. If the configure-command option is used to define a custom configure command no automatic --prefix injection takes place. You can also set the --prefix parameter explicitly in configure-options.

md5sum

MD5 checksum for the package file. If available the MD5 checksum of the downloaded package will be compared to this value and if the values do not match the execution of the recipe will fail.

make-binary

Path to the make program. Defaults to 'make' which should work on any system that has the make program available in the system PATH.

make-options

Extra KEY=VALUE options included in the invocation of the make program. Multiple options can be given on separate lines to increase readability.

make-targets

Targets for the make command. Defaults to 'install' which will be enough to install most software packages. You only need to use this if you want to build alternate targets. Each target must be given on a separate line.

configure-command

Name of the configure command that will be run to generate the Makefile. This defaults to ./configure which is fine for packages that come with a configure script. You may wish to change this when compiling packages with a different set up. See the Compiling a Perl package section for an example.

configure-options

Extra options to be given to the configure script. By default only the --prefix option is passed which is set to the part directory. Each option must be given on a separate line.

patch-binary

Path to the patch program. Defaults to 'patch' which should work on any system that has the patch program available in the system PATH.

patch-options

Options passed to the patch program. Defaults to -p0.

patches

List of patch files to the applied to the extracted source. Each file should be given on a separate line.

pre-configure-hook

Custom python script that will be executed before running the configure script. The format of the options is:

/path/to/the/module.py:name_of_callable

where the first part is a filesystem path to the python module and the second part is the name of the callable in the module that will be called. The callable will be passed three parameters in the following order:
The options dictionary from the recipe.
The global buildout dictionary.
A dictionary containing the current os.environ augmented with the part specific overrides.
The callable is not expected to return anything.

Note

The os.environ is not modified so if the hook script is interested in the environment variable overrides defined for the part it needs to read them from the dictionary that is passed in as the third parameter instead of accessing os.environ directly.

pre-make-hook

Custom python script that will be executed before running make. The format and semantics are the same as with the pre-configure-hook option.

post-make-hook

Custom python script that will be executed after running make. The format and semantics are the same as with the pre-configure-hook option.

keep-compile-dir

Switch to optionally keep the temporary directory where the package was compiled. This is mostly useful for other recipes that use this recipe to compile a software but wish to do some additional steps not handled by this recipe. The location of the compile directory is stored in options['compile-directory']. Accepted values are true or false, defaults to false.

environment-section

Name of a section that provides environment variables that will be used to augment the variables read from os.environ before executing the recipe.

This recipe does not modify os.environ directly. External commands run as part of the recipe (e.g. make, configure, etc.) get an augmented environment when they are forked. Python hook scripts are passed the augmented as a parameter.

The values of the environment variables may contain references to other existing environment variables (including themselves) in the form of Python string interpolation variables using the dictionary notation. These references will be expanded using values from os.environ. This can be used, for example, to append to the PATH variable, e.g.:

[component]
recipe = hexagonit.recipe.cmmi
environment-section =
    environment

[environment]
PATH = %(PATH)s:${buildout:directory}/bin
environment

A sequence of KEY=VALUE pairs separated by newlines that define additional environment variables used to update os.environ before executing the recipe.

The semantics of this option are the same as environment-section. If both environment-section and environment are provided the values from the former will be overridden by the latter allowing per-part customization.

Additionally, the recipe honors the download-cache option set in the [buildout] section and stores the downloaded files under it. If the value is not set a directory called downloads will be created in the root of the buildout and the download-cache option set accordingly.

The recipe will first check if there is a local copy of the package before downloading it from the net. Files can be shared among different buildouts by setting the download-cache to the same location.
