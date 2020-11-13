import os
from flask import Flask, request, jsonify, render_template
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin


ENV = str(os.environ.get('ENV', 'developement'))
# init
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


if ENV == 'production':
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:KrCBxEPyMigpBg03@35.231.61.14/budgetapp'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:super123@localhost/budgetapp'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
budgetOperation_schema = BudgetOperationSchema()
budgetOperations_schema = BudgetOperationSchema(many=True)


# create operation
@app.route('/operation', methods=['POST'])
def createOperation():
    name = request.json['name']
    value = request.json['value']
    schedule_id = request.json['schedule_id']

    new_operation = BudgetOperation(value, name)
    new_operation.schedule_id = schedule_id

    db.session.add(new_operation)
    db.session.commit()
    return budgetOperation_schema.jsonify(new_operation)


# update operation
@app.route('/operation/<id>', methods=['PUT'])
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

    return budgetOperation_schema.jsonify(operation)


# get all operations
@app.route('/operation', methods=['GET'])
def getOperations():
    all_operations = BudgetOperation.query.all()
    result = budgetOperations_schema.dump(all_operations)
    return jsonify(result)

# get single operation


@app.route('/operation/<id>', methods=['GET'])
def getOperation(id):
    operation = BudgetOperation.query.get(id)
    return budgetOperation_schema.jsonify(operation)


# delete operation
@app.route('/operation/<id>', methods=['DELETE'])
def deleteOperation(id):
    operation = BudgetOperation.query.get(id)
    db.session.delete(operation)
    db.session.commit()
    return budgetOperation_schema.jsonify(operation)


@app.route('/')
@cross_origin()
def render_test_page():
    return render_template('index.html')


# run server
if __name__ == '__main__':

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
