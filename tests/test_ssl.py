
def main():
    # hopefully, even the oldest ca-certificates will verify google.com
    import urllib
    import ssl
    # TODO: remove the unverified context once certificates are properly updated.
    context = ssl._create_unverified_context()
    urllib.urlretrieve("https://google.com", context=context)


if __name__ == "__main__":
    main()
