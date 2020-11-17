from flask import Flask
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin

from middleware.tokenAuth import requires_auth, AuthError
from flask_restful import Api


from app.configs import Config, Configdb

app = Flask(__name__)

app.config.from_object(Config)
app.config.from_object(Configdb)

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
api = Api(app)
cors = CORS(app)


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# create all db tables


def create_app():
    """Application-factory pattern"""
    #print('INIT-app: db.init_app(app)')
    # db.init_app(app)
    print('INIT-app: migrate.init_app(app, db)')
    migrate.init_app(app, db)
    return app


@app.before_first_request
def create_tables():
    import models
    print('app -> calls db.create_all() ')
    db.create_all()
