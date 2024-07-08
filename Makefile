PREFIX  = /opt/infinidat
TOOLKIT = $(PREFIX)/toolkit

export PATH = $(TOOLKIT)/bin:/bin:/usr/bin:/sbin:/usr/sbin
export SSL_CERT_FILE = $(TOOLKIT)/etc/ssl/certs/ca-bundle.crt

all: build pack

build:
	uname -a
	echo PATH=$(PATH)
	python --version
	buildout bootstrap
	bin/buildout
	bin/build

pack:
	bin/pack
