
Introduction
============

This project builds a portable Python interpreter, along with all the shared libraries it depends on.
The build system itself is written in Python, based on zc.buildout and some recipes.

The sources are downloaded from the Internet, stored locally and then built.

The current supported platforms are: Linux, OS X, Windows, Solaris and AIX.

In order to build python, execute:

    pip install zc.buildout
    buildout bootstrap
    ./bin/buildout
    ./bin/build

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
* Microsot Visual Studio 2010 (No SP)
* Perl
* Python
