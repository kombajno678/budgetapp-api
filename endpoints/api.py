from app import db, ma

from flask_restful import Resource
#from http import client
from flask import jsonify


class RootApi(Resource):
    MODEL_CLASS = None

    def get(self, *args, **kwargs):
        if self.MODEL_CLASS == None:
            return jsonify('ok')

        #query = self.model_query(db, **kwargs)

        if kwargs.get("id"):
            # get single element
            id = kwargs.get('id')
            element = self.MODEL_CLASS.query.get(id)
            return self.MODEL_CLASS.Schema().jsonify(element)
        else:
            elements = self.MODEL_CLASS.query.all()
            result = self.MODEL_CLASS.Schema(many=True).dump(elements)
            return jsonify(result)

    def delete(self, **kwargs):
        pass

    def post(self, **kwargs):
        pass

    def put(self, **kwargs):
        pass

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
