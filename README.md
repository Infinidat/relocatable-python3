
Introduction
============

This project builds a portable Python interpreter, along with all the shared libraries it depends on.
The build system itself is written in Python, based on zc.buildout and some recipes.

The sources are downloaded from the Internet, stored locally and then built.

The current supported platforms are: Linux, macOS, Windows, Solaris and AIX.

In order to build python, execute:

    make

Or, for Windows:

    nmake -f Makefile.win

Build environment
=================

You'll need to have pip installed on the build environment.

For building on macOS, you'll need to install:
* Xcode command line tools
* Homebrew

```
brew install automake autoconf libtool
```

For Ubuntu, you'll need to install:
* build-essential

For Windows, you'll need to install:
* Microsot Visual Studio 2017 (No SP)
* Microsoft Windows SDK 10
* Perl
* Python
