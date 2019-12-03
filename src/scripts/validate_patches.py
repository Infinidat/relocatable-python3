import os
from glob import glob
from subprocess import check_call


def main():
    if os.name == 'nt':
        return

    patch_files = glob(os.path.join(os.getcwd(), "src/patches", "python-3*.patch"))
    for file in patch_files:
        print('Validating patch: ' + file)
        check_call(['patch', '-d', '../', '--dry-run', '-p0', '-i', file])
        print('')
    print('\n\nAll patches were validated correctly')


if __name__ == "__main__":
    main()
