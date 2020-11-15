import os
from flask import Flask, request, jsonify, render_template, _request_ctx_stack, url_for
from flask_cors import cross_origin

from middleware.tokenAuth import AuthError

from models import *

from app import create_app, db, api, migrate
#from endpoints.api import RootApi
from endpoints import routes
#from endpoints.users.api import UserApi
#from endpoints.users.operations.api import OperationApi

ENV = str(os.environ.get('ENV', 'developement'))


app = create_app()


@app.route('/')
@cross_origin()
def render_test_page():
    return jsonify({"msg": 'hello, budgetappi works!'})


'''
@app.route('/testtoken')
@cross_origin()
@requires_auth
def test_token():
    return jsonify(_request_ctx_stack.top.current_user)
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return jsonify(links)


#api.add_resource(RootApi, '/api', endpoint='api')
#api.add_resource(UserApi, '/users', '/users/', endpoint='main')

if __name__ == "__main__":

    print('ENV=' + str(os.environ.get('ENV')))
    print('FLASK_APP=' + str(os.environ.get('FLASK_APP')))
    print('DATABASE_URL=' + str(os.environ.get('DATABASE_URL')))
    print('AUTH0_DOMAIN=' + str(os.environ.get('AUTH0_DOMAIN')))
    print('API_IDENTIFIER=' + str(os.environ.get('API_IDENTIFIER')))

    print('INIT: app startup, ENV : ' + str(ENV))

    try:
        print('INIT: db connection test  :  ' +
              str(db.session.query('1').first()))
    except:
        print('INIT: db connection test error')

    print('INIT: app.run()')

    app.run(host='0.0.0.0')
