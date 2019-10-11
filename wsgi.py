from ajnaapi.main import create_app

if __name__ == '__main__':
    app = create_app()  # pragma: no cover
    print(app.url_map)  # pragma: no cover
    app.run(port=5004, threaded=False, debug=True)
