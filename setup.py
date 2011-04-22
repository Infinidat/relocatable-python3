from setuptools import setup as _setup
from setuptools import find_packages

SETUP_INFO = dict(
    name = 'hello',
    version = '0.1',
    author = 'Infinidat',
    description = 'hello world',
    long_description = (),
    classifiers = [],
    install_requires = [],
    extras_require = {},

    test_suite = '',
    tests_require = {},

    namespace_packages = ['hello', ],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,

    entry_points = dict(
        console_scripts = [
            'script = hello:script.main'],
        gui_scripts = [])

    )

def setup():
    _setup(**SETUP_INFO)
if __name__ == '__main__':
    setup()


