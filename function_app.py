@app.route(route="http_trigger1")
def http_trigger1(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name test')

    if name:
        return func.HttpResponse(f"Hello, Atom space {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "Atom space. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
