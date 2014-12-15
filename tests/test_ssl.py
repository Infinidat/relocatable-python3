
def main():
    # hopefully, even the oldest ca-certificates will verify google.com
    import urllib
    urllib.urlretrieve("https://google.com")


if __name__ == "__main__":
    main()
