import setuptools

SETUP_INFO = dict(
    name = 'python',
    version = '3.11.15',
    author = 'Infinidat',
    description = 'Build Relocatable Python',
    long_description = 'Build Relocatable Python',
    install_requires = [
        'infi.gitpy>=1.0.7',
        'infi.os_info>=0.1.22',
        'infi.recipe.python>=0.6.28',
        'setuptools>=43.0.0'
    ],
    packages = setuptools.find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    entry_points = dict(
        console_scripts = [
            'clean = scripts:clean',
            'build = scripts:build',
            'pack = scripts:pack'
        ],
        gui_scripts = []
    )
)

def setup():
    setuptools.setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()
