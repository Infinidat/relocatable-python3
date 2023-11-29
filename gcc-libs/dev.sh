mkdir -p /root/src/relocatable-python3/dist/lib
cd /home/opt/dev/lib/pthread/ppc64 && \
tar cvf - libgcc_s.so* libstdc++*.so*| (cd /root/src/relocatable-python3/dist/lib/ && tar xvf -)
rm -f /root/src/relocatable-python3/dist/lib/*.py
