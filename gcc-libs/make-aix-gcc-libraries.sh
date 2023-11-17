#!/bin/bash

set -exu

DEFAULT_AR='ar -X64'
DEFAULT_CC='gcc'
DEFAULT_CFLAGS='-maix64'
DEFAULT_LIBPATH='dist/lib'

AR=${AR:-$DEFAULT_AR}
CC=${CC:-$DEFAULT_CC}
CFLAGS=${CFLAGS:-$DEFAULT_CFLAGS}
LIBPATH=${LIBPATH:-$DEFAULT_LIBPATH}

LIBGCC=$($CC $CFLAGS -pthread -print-file-name=libgcc_s.a)
LIBSTD=$($CC $CFLAGS -pthread -print-file-name=libstdc++.a)

rm -f shr.o libgcc_s.so.1 libgcc_s.so
$AR -xv $LIBGCC

rm -f libstdc++.so.6 libstdc++.so
$AR -xv $LIBSTD

mkdir -p $LIBPATH
chmod 0755 $LIBPATH
chmod 0444 *.*o*
mv shr.o $LIBPATH/libgcc_s.so.1
ln -s libgcc_s.so.1 $LIBPATH/libgcc_s.so
mv libstdc++.so.6 $LIBPATH/libstdc++.so.6
ln -s libstdc++.so.6 $LIBPATH/libstdc++.so
