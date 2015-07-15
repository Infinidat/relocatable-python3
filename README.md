
Introduction
============

This project builds a portable Python interpreter, along with all the shared libraries it depends on.
The build system itself is written in Python, based on zc.buildout and some recipes.

The sources are downloaded from the Internet, stored locally and then built.

The current supported platforms are: Linux, OS X, Windows, Solaris and AIX.

In order to build python, execute:

    python bootstrap.py
    ./bin/buildout
    ./bin/build

**For Python 3.x, see [relocatable-python3](https://github.com/Infinidat/relocatable-python3)**

Build environment
=================

For building on Mac OS X, you'll need to install first:
* Xcode command line tools
* Homebrew
* autoconf, automake, libtool, pkgconfig

For Ubuntu, you'll need to install:
* build-essential

For Windows, you'll need to install:
* Microsot Visual Studio 2008 (No SP)
* Perl
* Python
