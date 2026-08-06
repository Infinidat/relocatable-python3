all: build pack

build:
	uname -a
	python --version
	buildout bootstrap
	bin/buildout
	bin/build

pack:
	bin/pack

clean:
	bin/clean
