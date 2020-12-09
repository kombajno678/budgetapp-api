import functools
from logging import error
import os
import json
from werkzeug.utils import secure_filename
import pandas as pd
from flask import Flask, request, jsonify, render_template, _request_ctx_stack, url_for, after_this_request
from flask_cors import cross_origin

from middleware.tokenAuth import AuthError, requires_auth
from models import *
from app import create_app, db, api, migrate
from endpoints import routes

import gzip
import functools
from io import BytesIO as IO

from analyzer import Analyzer

ENV = str(os.environ.get('ENV', 'developement'))


app = create_app()
if(ENV == 'developement'):
    dirname = os.path.dirname(__file__)

    app.config['UPLOAD_FOLDER'] = os.path.join(dirname, 'tmp')
else:
    app.config['UPLOAD_FOLDER'] = '/tmp'


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                    'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func


@app.route('/')
@cross_origin()
def render_test_page():
    return jsonify({"msg": 'hello, budgetappi works!'})


@app.route('/testtoken')
@cross_origin()
@requires_auth
def test_token():
    return jsonify(_request_ctx_stack.top.current_user)


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


ALLOWED_EXTENSIONS = {'csv', 'txt'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
@gzipped
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return 'None', 400
    file = request.files['file']
    if file.filename == '':
        return 'None', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print('file.save ' + str(filepath))
        file.save(filepath)
        try:
            ops, sops, cats = loadMBankCsv(filepath)
            # print(df)
            ops_json = '['
            sops_json = '['
            cats_json = '['

            for x in ops:
                ops_json += json.dumps(x.to_dict(_path="operation",
                                                 _hide=[])) + ','
            #ops_json += json.dumps(ops.to_dict())
            ops_json = ops_json[:-1] + ']'

            for x in sops:
                sops_json += json.dumps(
                    x.to_dict(_path="scheduled_operation", _hide=[])) + ','
            #sops_json += json.dumps(sops.to_dict())
            sops_json = sops_json[:-1] + ']'

            for x in cats:
                cats_json += json.dumps(x.to_dict(_path="category",
                                                  _hide=[])) + ','
            #cats_json += json.dumps(cats.to_dict())
            cats_json = cats_json[:-1] + ']'

            report = '{"Operations":%s, "ScheduledOperations":%s, "Categories":%s}' % (
                ops_json, sops_json, cats_json)

            return str(report), 200
        except error:
            return str(error), 500
    else:
        return 'None', 400


def loadMBankCsv(file):
    a = Analyzer(filePath=file)
    a.analyzeOperationsFromCsv()
    return a.operationsToAdd, a.scheduledOperationsToAdd, a.categoriesToAdd


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
