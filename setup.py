
SETUP_INFO = dict(
    name = 'python',
    version = '0.1',
    author = 'Infinidat',
    description = 'builds python',
    long_description = (),
    classifiers = [],
    install_requires = ['setuptools', 'infi.execute'],
    extras_require = {},

    test_suite = '',
    tests_require = {},

    packages = [],
    package_dir = {'': 'src'},
    include_package_data = True,

    entry_points = dict(
        console_scripts = [
			'build = scripts:build',
			'pack = scripts:pack',
            'clean = scripts:clean',
        ],
        gui_scripts = [])

    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

