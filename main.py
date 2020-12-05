from logging import error
from old_app import BudgetOperation
import os
from werkzeug.utils import secure_filename
import pandas as pd
from flask import Flask, request, jsonify, render_template, _request_ctx_stack, url_for
from flask_cors import cross_origin

from middleware.tokenAuth import AuthError, requires_auth
from models import *
from app import create_app, db, api, migrate
from endpoints import routes

ENV = str(os.environ.get('ENV', 'developement'))


app = create_app()
if(ENV == 'developement'):
    dirname = os.path.dirname(__file__)

    app.config['UPLOAD_FOLDER'] = os.path.join(dirname, 'tmp')
else:
    app.config['UPLOAD_FOLDER'] = '/tmp'


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


@app.route('/uploads', methods=['POST'])
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
            df = loadMBankCsv(filepath)
            # print(df)

            # TODO: delete uploaded file

            return str(df.to_json(orient='index')), 200
        except error:
            return str(error), 500
    else:
        return 'None', 400


def loadMBankCsv(file):
    # check if 'zestawienie' or 'lista' operacji
    linesToSkip = 0

    fs = open(file, 'r', encoding='cp1250')
    for txt_line in fs:
        print(txt_line)
        if(txt_line.lower().__contains__("#data operacji")):
            print("found start at line : " + str(linesToSkip))
            break
        linesToSkip += 1

    fs.close()

    parsed = pd.read_csv(file, sep=';', encoding='cp1250', skip_blank_lines=False,
                         skiprows=linesToSkip, header=0, index_col=False, decimal=",")

    for c in parsed.columns:
        print(str(c))

    for x in parsed.values:
        temp = Operation()
        temp.name = x[1]
        temp.value = x[4]
        temp.when = x[0]
        for val in x:
            print(str('x') + ' - ' + str(val))
    # parsed.shape[0] = length; #parsed.columns:PandasArray
    # Data operacji
    # Opis operacji
    # Tytuł ?
    # Kwota
    # Kategoria ?

    return parsed


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
