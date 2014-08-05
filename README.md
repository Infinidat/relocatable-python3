
Introduction
============

This project builds a portable Python interpreter, along with all the shared libraries it depends on.
The build system itself is written in Python, based on zc.buildout and some recipes.

The sources are downloaded from the Internet, stored locally and then built.

It works on Linux, OSX and Windows for now.

In order to build python, execute:

$ python bootstrap.py
$ ./bin/buildout
$ ./bin/build

Build environment
=================

For building on Mac OS X, you'll need to install first:
* Xcode command line tools
* Homebrew
* autoconf, automake, libtool, pkgconfig

For ubuntu, you'll need to install:
* build-essential

For windows, you'll need to install:
* Microsot Visual Studio 2008 (No SP)
* Microsot Visual Studio 2010 (No SP)
* Perl
* Python
