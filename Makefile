SHELL         := /bin/bash
UNAME         := $(shell uname)

ifeq ($(findstring CYGWIN,$(UNAME)),CYGWIN)
TARGET        := windows
PATH          := $(CURDIR)/dist/python/bin:$(CURDIR)/dist/python/Scripts:$(PATH)
SSL_CERT_URL  := https://curl.se/ca/cacert.pem
SSL_CERT_FILE := $(CURDIR)/dist/ca-bundle.crt
PYTHON_URL    := http://python.infinidat.com/packages/main-stable/python/python-v3.11.9-windows-x64.tar.gz
GET_PIP_URL   := https://bootstrap.pypa.io/get-pip.py
else
TARGET        := unix
PREFIX        := /opt/infinidat
TOOLKIT       := $(PREFIX)/toolkit
PATH          := $(TOOLKIT)/bin:/bin:/usr/bin:/sbin:/usr/sbin
SSL_CERT_FILE := $(TOOLKIT)/etc/ssl/certs/ca-bundle.crt
endif

.PHONY: all build pack

all: $(TARGET) build pack

windows: dist/.done

dist/.done:
	rm -rf dist
	mkdir -p dist
	curl -s -k -L -o $(SSL_CERT_FILE) $(SSL_CERT_URL)
	curl -s -k -L -o dist/python.tar.gz $(PYTHON_URL)
	tar xf dist/python.tar.gz -C dist
	curl -s -k -L -o dist/get-pip.py $(GET_PIP_URL)
	dist/python/bin/python dist/get-pip.py --quiet
	dist/python/Scripts/pip3 install --quiet infi.projector
	touch dist/.done

unix:
	gcc -v

build:
	uname -a
	python --version
	projector --version
	buildout bootstrap
	bin/buildout
	bin/build

pack:
	bin/pack
