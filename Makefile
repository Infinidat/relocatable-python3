make:
	pip install zc.buildout distro
	pip install setuptools==49.2.1 --upgrade -i https://pypi.org/simple
	buildout bootstrap
	bin/buildout
	bin/build

pack:
	bin/pack