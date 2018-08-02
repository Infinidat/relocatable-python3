
Introduction
============

This project builds a portable Python interpreter, along with all the shared libraries it depends on.
The build system itself is written in Python, based on zc.buildout and some recipes.

The sources are downloaded from the Internet, stored locally and then built.

The current supported platforms are: Linux, OS X, Windows, Solaris and AIX.

In order to build python, execute:

    pip install zc.buildout
    buildout bootstrap
    bin/buildout
    bin/build

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


Caveats
=======

* cyrus-sasl is compiled without GSSAPI support on solaris systems
* gnutls, gcryct, gpg-error, nettle, gmp have been removed, now using only openssl as SSL backend
* Link time optimiziation and profile guided optimization flags ar eused only on ubuntu, osx, windows, arch.
* missing _dbm in python is OK because we are compiling with gdbm.
* Solaris platforms doesn't support ossaudiodev in python3
* UUID capabilites is provided by a 3rd-party library extract from linux-utils