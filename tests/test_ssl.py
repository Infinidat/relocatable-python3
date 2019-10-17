def main():
    # hopefully, even the oldest ca-certificates will verify google.com
    from urllib import request
    response = request.urlopen("https://google.com")
    assert(response.getcode() == 200)

if __name__ == "__main__":
    main()
