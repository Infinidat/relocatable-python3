
def main():
    # hopefully, even the oldest ca-certificates will verify google.com
    import urllib
    # TODO: remove verify=False once certificates are properly updated.
    urllib.urlretrieve("https://google.com", verify=False)


if __name__ == "__main__":
    main()
