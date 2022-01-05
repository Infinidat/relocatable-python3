make:
	pip install zc.buildout distro
	pip install setuptools==49.2.1 --upgrade -i https://pypi.org/simple
	buildout bootstrap
	bin/buildout
	bin/build

pack:
	bin/pack

test:
ifneq ("$(wildcard dist/bin/python.exe)","")
	dist/bin/python.exe tests/test_ssl.py
	dist/bin/python.exe tests/test_dynload_imports.py
	dist/bin/python.exe tests/test_readline.py
	dist/bin/python.exe tests/test_subprocess.py
else
	dist/bin/python3 tests/test_ssl.py
	dist/bin/python3 tests/test_dynload_imports.py
	dist/bin/python3 tests/test_readline.py
	dist/bin/python3 tests/test_subprocess.py
endif

