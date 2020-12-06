import os
from flask import Flask, flash, request, render_template, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import pandas as pd
ENV = str(os.environ.get('ENV','dev'))

UPLOAD_FOLDER_prod = '/tmp'
UPLOAD_FOLDER_dev = 'uploads'

ALLOWED_EXTENSIONS = {'csv', 'txt'}


app = Flask(__name__)
api = Api(app)
ma = Marshmallow(app)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'





# db config

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/flask-test'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_dev
else:
    app.debug = False
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ueskuahwmobatn:f9cf075ac7555e72e100e45faae5f93588aaed25fe2e826a12f65a41755ed356@ec2-54-247-94-127.eu-west-1.compute.amazonaws.com:5432/d58b1gfhhttkv1'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:KrCBxEPyMigpBg03@35.231.61.14/budgetapp'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_prod

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class BudgetModel(db.Model):
    __tablename__ = 'budget'

    id = db.Column(db.Integer, primary_key=True)
    initialBudget = db.Column(db.Float)
    monthlyExpenses = db.Column(db.Float)
    monthlyIncome = db.Column(db.Float)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def __init__(self, initialBudget, monthlyExpenses, monthlyIncome):
        
        self.initialBudget = initialBudget
        self.monthlyExpenses = monthlyExpenses
        self.monthlyIncome = monthlyIncome
    
    def __repr__(self):
        return '<BudgetModel; ' + str(self.initialBudget) + '; ' + str(self.monthlyExpenses) + '; ' + str(self.monthlyIncome) + '>'


class BudgetSchema(ma.Schema):
    class Meta:
        fields = ("id", "initialBudget", "monthlyExpenses", "monthlyIncome", "created", "updated")
        model = BudgetModel

budget_schema = BudgetSchema()
budgets_schema = BudgetSchema(many=True)



class BudgetResource(Resource):
    def get(self):
        if request.json and 'id' in request.json:
            find_id = request.json['id']
            budget = BudgetModel.query.get(find_id)
            return budget_schema.dump(budget)
        else:
            budgets = BudgetModel.query.all()
            return budgets_schema.dump(budgets)
            
    def put(self):
        new_budget = BudgetModel(
            initialBudget = request.json['initialBudget'],
            monthlyExpenses = request.json['monthlyExpenses'],
            monthlyIncome = request.json['monthlyIncome']
        )
        db.session.add(new_budget)
        db.session.commit()
        return budget_schema.dump(new_budget)

    def delete(self, budget_id):
        budget_to_delete = BudgetModel.query.get_or_404(budget_id)
        db.session.delete(budget_to_delete)
        db.session.commit()
        return '', 204

    def patch(self):
        id = request.json['id']
        budget = BudgetModel.query.get_or_404(id)

        if 'initialBudget' in request.json:
            budget.initialBudget = request.json['initialBudget']

        if 'monthlyExpenses' in request.json:
            budget.monthlyExpenses = request.json['monthlyExpenses']

        if 'monthlyIncome' in request.json:
            budget.monthlyIncome = request.json['monthlyIncome']
        
        db.session.commit()
        return budget_schema.dump(budget)

api.add_resource(BudgetResource, '/budget', '/budget/<int:budget_id>')

@app.route('/')
@cross_origin()
def render_test_page():
    return render_template('index.html')


@app.route('/create')
@cross_origin()
def create():
    db.create_all()
    return {"result" : "how tf should i know"}






def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print('file.save ' + str(filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            try:
                df = loadMBankCsv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                print(df)
                return str(df.to_json(orient='index'))
            except:
                print('error at : loadMBankCsv(file)')


            #return redirect(url_for('uploaded_file', filename=filename))
            return 'nok'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def loadMBankCsv(file):
    return pd.read_csv(file, sep=';', encoding='cp1250', skip_blank_lines=False, skiprows=25, header=0, index_col=False)


if(__name__ == "__main__"):

    print('app startup, ENV : ' + str(ENV))
    
    if ENV == 'dev':
        try:
            print('select 1  :  ' + str(db.session.query('1').first()))
        except:
            print('no db connection')
        
    try:
        db.create_all()
    except:
        print('error at: db.create_all()')
    
    app.run()

