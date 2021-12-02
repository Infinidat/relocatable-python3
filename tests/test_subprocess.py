def main():
    import subprocess
    import sys
    res = subprocess.run([sys.executable, "tests/test_dynload_imports.py"])
    assert(res.returncode == 0)


if __name__ == "__main__":
    main()
