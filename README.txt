
Introduction
============

This project builds a portable Python interpreter, along with all the shared libraries it depends on.
The build system itself is written in Python, based on zc.buildout and some recipes.

The sources are downloaded from the Internet, stored locally and then built.

It works on Linux and OSX for now.

In order to build python, execute:

$ python bootstrap.py
$ ./bin/buildout
$ ./bin/build

