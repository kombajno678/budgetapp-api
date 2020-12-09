from app import db, ma

from flask_restful import Resource
#from http import client
from flask import jsonify, _request_ctx_stack, request
from middleware.tokenAuth import requires_auth


from models.User import User


class RootApi(Resource):
    MODEL_CLASS = None

    @requires_auth
    def get(self, *args, **kwargs):
        if self.MODEL_CLASS == None:
            return jsonify('ok')

        user_auth_id = _request_ctx_stack.top.current_user
        # get user
        user = User.getByAuthId(user_auth_id)
        if user is None:
            print('User.getByAuthId(user_auth_id) is None, ' + str(user_auth_id))
            return None, 401

        query = self.model_query(db, user.id)

        if kwargs.get("id"):
            # get single element
            id = kwargs.get('id')
            element = query.get_or_404(id)
            return self.MODEL_CLASS.Schema().jsonify(element)
        else:
            elements = query.all()
            result = self.MODEL_CLASS.Schema(many=True).dump(elements)
            return jsonify(result)

    @requires_auth
    def delete(self, **kwargs):
        if self.MODEL_CLASS == None:
            return jsonify('ok')

        # check if this user can delete this object

        #query = self.model_query(db, **kwargs)

        user_auth_id = _request_ctx_stack.top.current_user
        user = User.getByAuthId(user_auth_id)

        if user is None:
            return None, 401

        if kwargs.get("id") is not None and kwargs.get("id") != 0:

            if kwargs.get('id') is None:
                return None, 400

            query = self.model_query(db, user.id, **kwargs)
            existing_object = query.filter(
                self.MODEL_CLASS.id == kwargs.get('id')).first()

            if existing_object is None:
                return None, 404

            db.session.delete(existing_object)
            db.session.commit()
            return self.MODEL_CLASS.Schema().jsonify(existing_object)
        else:

            # http req body values
            if isinstance(request.json, list):
                # do stuff is list is passed in request
                # deleting multiple items
                query = self.model_query(db, user.id, **kwargs)
                existing_objects = query.filter(
                    self.MODEL_CLASS.id in request.json).first()

                if existing_objects is None or len(existing_objects) == 0:
                    return None, 404

                db.session.delete(existing_objects)
                db.session.commit()
                return len(existing_objects), 200

            else:
                return None, 400

            return None, 400

    @requires_auth
    def post(self, **kwargs):
        user_auth_id = _request_ctx_stack.top.current_user
        user = User.getByAuthId(user_auth_id)

        if user is None:
            return None, 401

        # http req body values
        if isinstance(request.json, list):
            print('posting multiple items')
            new_objects = []

            for obj in request.json:
                new_object = self.MODEL_CLASS()
                for key, value in obj.items():
                    if hasattr(new_object, key):
                        setattr(new_object, key, value)
                # user FK
                if hasattr(new_object, 'user_id'):
                    setattr(new_object, 'user_id', user.id)
                # make sure PK is null
                new_object.id = None
                db.session.add(new_object)
                new_objects.append(new_object)
            # print(new_objects)
            try:
                db.session.commit()
                return self.MODEL_CLASS.Schema(many=True).jsonify(new_objects)
            except Exception as err:
                print(err)
                return None, 400
        else:
            print('posting single item')
            new_object = self.MODEL_CLASS()
            for key, value in request.json.items():
                if hasattr(new_object, key):
                    setattr(new_object, key, value)
            # user FK
            if hasattr(new_object, 'user_id'):
                setattr(new_object, 'user_id', user.id)
            # make sure PK is null
            new_object.id = None
            db.session.add(new_object)

            try:
                db.session.commit()
                return self.MODEL_CLASS.Schema().jsonify(new_object)
            except Exception as err:
                print(err)
                return None, 400

    @requires_auth
    def put(self, **kwargs):
        user_auth_id = _request_ctx_stack.top.current_user
        user = User.getByAuthId(user_auth_id)

        if user is None:
            return None, 401

        if kwargs.get('id') is None:
            return None, 400

        query = self.model_query(db, user.id, **kwargs)

        existing_object = query.filter(
            self.MODEL_CLASS.id == kwargs.get('id')).first()

        if existing_object is None:
            return None, 404

        # http req body values
        for key, value in request.json.items():
            if key == 'id' or key == 'user_id':
                continue
            if hasattr(existing_object, key):
                setattr(existing_object, key, value)

        try:
            db.session.commit()
            return self.MODEL_CLASS.Schema().jsonify(existing_object)
        except Exception as err:
            print(err)
            return None, 400

        """
        Handle a GET request.
        """
        '''
        try:
            #db = db_connect()
            query = self.model_query(db, **kwargs)

            if kwargs.get("id"):
                # take the broad query and apply an identifier filter
                query = query.filter(
                    self.MODEL_CLASS.id == kwargs["id"]
                )

                model = query.first()

                if not model:
                    # identifier not found
                    return {
                        "id": kwargs["id"]
                    }, client.NOT_FOUND

                # return single model result in JSON format
                return model.to_json(), client.OK

            # return page of model results in JSON format
            return [
                model.to_json() for model in query
            ], client.OK
        except:
            db and db.rollback()

            # oops
            return "", client.INTERNAL_SERVER_ERROR
        finally:
            db and db.close()
        '''

        """
        Handle a DELETE request.
        """
        '''
        try:
            #db = db_connect()
            query = self.model_query(db, **kwargs)
            query = query.filter(
                self.MODEL_CLASS.id == kwargs["id"]
            )

            model = query.first()

            if not model:
                # identifier not found
                return {
                    "id": kwargs["id"]
                }, client.NOT_FOUND

            model.delete()
            db.commit()

            return {
                "id": kwargs["id"]
            }, client.ACCEPTED
        except:
            db and db.rollback()

            # oops
            return "", client.INTERNAL_SERVER_ERROR
        finally:
            db and db.close()
        '''
