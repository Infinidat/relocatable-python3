make:
	pip install zc.buildout distro
	buildout bootstrap
	bin/buildout
	bin/build

pack:
	bin/pack