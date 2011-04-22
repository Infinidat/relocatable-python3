from setuptools import setup as _setup
from setuptools import find_packages

SETUP_INFO = dict(
    name = 'python_dist',
    version = '0.1',
    author = 'Infinidat',
    description = 'builds python',
    long_description = (),
    classifiers = [],
    install_requires = [],
    extras_require = {},

    test_suite = '',
    tests_require = {},

    packages = [],
    package_dir = {},
    include_package_data = True,

    entry_points = dict(
        console_scripts = [],
        gui_scripts = [])

    )

def setup():
    _setup(**SETUP_INFO)
if __name__ == '__main__':
    setup()


