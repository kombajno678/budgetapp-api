import os

from flask import Flask, request, jsonify, render_template, _request_ctx_stack
from flask_cors import CORS, cross_origin

#from middleware.loggermiddleware import LoggerMiddleware
from middleware.tokenAuth import requires_auth, AuthError

from endpoints import api
print('appp.__name__ : ' + __name__)


# env variables

ENV = str(os.environ.get('ENV', 'developement'))
DATABASE_URL = str(os.environ.get(
    'DATABASE_URL', 'postgresql://postgres:super123@localhost/budgetapp'))

# app init
#app = Flask(__name__)
#app.wsgi_app = LoggerMiddleware(app.wsgi_app)

#app.config['SECRET_KEY'] = 'kCRg9r7la92Efm5xPQckmD2SICr3VnEmgcv-HuhwnTCJclD96K0UAHeb4xOZztjJ'
#app.config['CORS_HEADERS'] = 'Content-Type'
#app.debug = ENV != 'production'
#cors = CORS(app)


# Operation
if True:

    class BudgetOperation(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        value = db.Column(db.Float)
        name = db.Column(db.String(100))

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


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


# run server
if __name__ == '__main__':

    # for k, v in os.environ.items():
    #    print(f'    {k}={v}')

    print('ENV=' + str(os.environ.get('ENV')))
    print('DATABASE_URL=' + str(os.environ.get('DATABASE_URL')))
    print('AUTH0_DOMAIN=' + str(os.environ.get('AUTH0_DOMAIN')))
    print('API_IDENTIFIER=' + str(os.environ.get('API_IDENTIFIER')))

    print('INIT: app startup, ENV : ' + str(ENV))

    try:
        print('INIT: db connection test  :  ' +
              str(db.session.query('1').first()))
    except:
        print('INIT: db connection test error')

    # try:
    #     print('INIT: executing: db.create_all() ...')
    #     db.create_all()
    #     print('INIT: done')
    # except:
    #     print('INIT: error at: db.create_all()')

    print('INIT: app.run()')
    db.drop_all()
    db.create_all()

    app.run()
