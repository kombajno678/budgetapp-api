from ..api import RootApi
from models.User import User
from app import db
from middleware.tokenAuth import requires_auth
from flask import jsonify, _request_ctx_stack, request


class UserApi(RootApi):

    MODEL_CLASS = User

    def model_query(self, db, **kwargs):

        return User.query

    @requires_auth
    def get(self, **kwargs):
        user_auth_id = _request_ctx_stack.top.current_user

        # get by id
        if kwargs.get("id"):
            # get single element
            id = kwargs.get('id')
            element = self.MODEL_CLASS.query.get(id)
            if element is not None:
                return self.MODEL_CLASS.Schema().jsonify(element)

        # get by token auth_id
        existing_user = None
        try:
            existing_user = User.query.filter_by(auth_id=user_auth_id).first()#error when no db
        except Exception as e:
            print(e)
            return {"error" : str(e)}, 500
            
            
        if existing_user:
            return User.Schema().jsonify(existing_user)

        new_user = User()
        new_user.id = None
        new_user.auth_id = user_auth_id
        db.session.add(new_user)
        try:
            db.session.commit()
            return User.Schema().jsonify(new_user)
        except Exception as err:
            print(err)
            return None, 400

    @requires_auth
    def post(self, **kwargs):
        user_auth_id = _request_ctx_stack.top.current_user
        print('USER POST, user auth id = ' + str(user_auth_id))

        new_user = User()

        for key, value in request.json.items():
            if hasattr(new_user, key):
                setattr(new_user, key, value)

        new_user.id = None
        new_user.auth_id = user_auth_id

        try:
            db.session.add(new_user)#error when no db
        except Exception as e:
            print(e)
            return {"error" : str(e)}, 500
        
        try:
            db.session.commit()
            return self.MODEL_CLASS.Schema().jsonify(new_user)
        except Exception as err:
            print(err)
            return None, 400

    @requires_auth
    def put(self, **kwargs):
        user_auth_id = _request_ctx_stack.top.current_user
        print('USER PUT, user auth id = ' + str(user_auth_id))

        # get by token auth_id
        existing_user = None
        try:
            existing_user = User.query.filter_by(auth_id=user_auth_id).first()#error when no db
        except Exception as e:
            print(e)
            return {"error" : str(e)}, 500
        
        if existing_user:
            # update values
            for key, value in request.json.items():
                if hasattr(existing_user, key):
                    setattr(existing_user, key, value)

            try:
                db.session.commit()
                return User.Schema().jsonify(existing_user)
            except Exception as err:
                print(err)
                return None, 400

        else:
            print('trying to update non existing user')
            return None, 404

        new_user = User()
        new_user.id = None
        new_user.auth_id = user_auth_id
        db.session.add(new_user)
        try:
            db.session.commit()
            return User.Schema().jsonify(new_user)
        except Exception as err:
            print(err)
            return None, 400
