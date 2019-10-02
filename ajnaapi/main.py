from ajnaapi import create_app

app = create_app()  # pragma: no cover
print(app.url_map)  # pragma: no cover

if __name__ == '__main__':  # pragma: no cover
    app.run(port=5004, debug=True)
