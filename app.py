from jose import jwt
from six.moves.urllib.request import urlopen
import json
import os
from functools import wraps
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template, _request_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin

from loggermiddleware import LoggerMiddleware
# imports for PyJWT authentication
#import jwt


# env variables

AUTH0_DOMAIN = str(os.environ.get('AUTH0_DOMAIN', ''))
API_IDENTIFIER = str(os.environ.get('API_IDENTIFIER', ''))
ALGORITHMS = ["RS256"]

ENV = str(os.environ.get('ENV', 'developement'))
DATABASE_URL = str(os.environ.get(
    'DATABASE_URL', 'postgresql://postgres:super123@localhost/budgetapp'))

# app init
app = Flask(__name__)
app.wsgi_app = LoggerMiddleware(app.wsgi_app)

cors = CORS(app)
app.config['SECRET_KEY'] = 'kCRg9r7la92Efm5xPQckmD2SICr3VnEmgcv-HuhwnTCJclD96K0UAHeb4xOZztjJ'
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = ENV != 'production'


# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)


'''
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    year = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=True)
    day_of_month = db.Column(db.Integer, nullable=True)
    day_of_week = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Schedule: Y:' + str(self.year) + ' M:' + str(self.month) + ' Dm:' + str(self.day_of_month) + ' Dw:' + str(self.day_of_week) + '>'
'''


#API_AUDIENCE = 'https://budgetapp-api-694202137.herokuapp.com/'

# Error handler
# from: https://auth0.com/docs/quickstart/backend/python


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# Format error response and append status code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError({"code": "invalid_header",
                             "description":
                             "Invalid header. "
                             "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError({"code": "invalid_header",
                             "description":
                             "Invalid header. "
                             "Use an RS256 signed JWT Access Token"}, 401)

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience='https://dev-wkdk2hez.eu.auth0.com/api/v2/',
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )

            except Exception as err:
                print('error: ' + str(err))
                print('unverified_header : ' + str(unverified_header))
                raise AuthError({"code": "invalid_header (other error)",
                                 "err": str(err)}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)
    return decorated


# decorator for verifying the JWT
'''
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        tokenString = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            tokenString = request.headers['Authorization']
        # return 401 if token is not passed
        if not tokenString:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            token = jwt.decode(tokenString, app.config['SECRET_KEY'])

        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(token, *args, **kwargs)

    return decorated
'''

# Operation


class BudgetOperation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    name = db.Column(db.String(100))

    '''
    schedule_id = db.Column(db.Integer, db.ForeingKey(
        'schedule.id'), nullable=True)
    schedule = db.relationship(
        'Schedule', backref=db.backref('budgetoperations', lazy=True))
    '''

    def __init__(self, value, name):
        self.value = value
        self.name = name

    def __repr__(self):
        # + ' schedule_id:' + str(self.schedule_id)
        return '<BudgetOperation: value:' + str(self.value) + ' name:' + str(self.name) + '>'
# Operation schema


class BudgetOperationSchema(ma.Schema):
    class Meta:
        fields = ('id', 'value', 'name', 'schedule_id')


# init schema
operation_schema = BudgetOperationSchema()
operations_schema = BudgetOperationSchema(many=True)


# create operation
@app.route('/operation', methods=['POST'])
@cross_origin()
@requires_auth
def createOperation():
    name = request.json['name']
    value = request.json['value']
    schedule_id = request.json['schedule_id']

    new_operation = BudgetOperation(value, name)
    new_operation.schedule_id = schedule_id

    db.session.add(new_operation)
    db.session.commit()
    return operation_schema.jsonify(new_operation)


# update operation
@app.route('/operation/<id>', methods=['PUT'])
@cross_origin()
@requires_auth
def updateOperation(id):
    # fetch
    operation = BudgetOperation.query.get(id)

    if request.json.__contains__('name'):
        operation.name = request.json['name']

    if request.json.__contains__('value'):
        operation.value = request.json['value']

    if request.json.__contains__('schedule_id'):
        operation.schedule_id = request.json['schedule_id']

    db.session.commit()

    return operation_schema.jsonify(operation)


# get all operations
@app.route('/operation', methods=['GET'])
@cross_origin()
@requires_auth
def getOperations():
    all_operations = BudgetOperation.query.all()
    result = operations_schema.dump(all_operations)
    return jsonify(result)

# get single operation


@app.route('/operation/<id>', methods=['GET'])
@cross_origin()
@requires_auth
def getOperation(id):
    operation = BudgetOperation.query.get(id)
    return operation_schema.jsonify(operation)


# delete operation
@app.route('/operation/<id>', methods=['DELETE'])
@cross_origin()
@requires_auth
def deleteOperation(id):
    operation = BudgetOperation.query.get(id)
    db.session.delete(operation)
    db.session.commit()
    return operation_schema.jsonify(operation)


@app.route('/')
@cross_origin()
def render_test_page():
    return render_template('index.html')


@app.route('/testtoken')
@cross_origin()
@requires_auth
def test_token():
    return jsonify(_request_ctx_stack.top.current_user)


# run server
if __name__ == '__main__':

    for k, v in os.environ.items():
        print(f'    {k}={v}')

    print('INIT: app startup, ENV : ' + str(ENV))

    try:
        print('INIT: db connection test  :  ' +
              str(db.session.query('1').first()))
    except:
        print('INIT: db connection test error')

    try:
        print('INIT: executing: db.create_all() ...')
        db.create_all()
        print('INIT: done')
    except:
        print('INIT: error at: db.create_all()')

    print('INIT: app.run()')

    app.run()
