def main():
    # hopefully, even the oldest ca-certificates will verify google's DNS
    from urllib import request
    response = request.urlopen("https://8.8.8.8")
    assert(response.getcode() == 200)

if __name__ == "__main__":
    main()
