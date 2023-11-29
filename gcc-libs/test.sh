#!/bin/bash

set -exu

root=$(gcc -print-search-dirs | awk '/^install/{print $NF}')

for arch in 32 64; do
  for type in '' -pthread; do
    lib=$(gcc -maix$arch $type -print-file-name=libgcc_s.a)
    dst=$(dirname $(gcc -maix$arch $type -print-file-name=libgcc_s.a | sed -e "s|^$root|dist/lib/|"))
    ar -X $arch -xv $lib
    mkdir -p $dst
    mv shr.o $dst/libgcc_s.so.1
    ln -s libgcc_s.so.1 $dst/libgcc_s.so

    lib=$(gcc -maix$arch $type -print-file-name=libstdc++.a)
    dst=$(gcc -maix$arch $type -print-file-name=libstdc++.a | sed -e "s|^$root|dist/lib/|")
    ar -X $arch -xv $lib
    mkdir -p $dst
    mv libstdc++.so.6 $dst/libstdc++.so.6
    ln -s libstdc++.so.6 $dst/libstdc++.so
  done
done
