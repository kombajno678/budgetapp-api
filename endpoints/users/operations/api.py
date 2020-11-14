from models.Operation import Operation
from models.User import User
from ...api import RootApi


class OperationApi(RootApi):

    MODEL_CLASS = Operation

    def model_query(self, db, user_id, **kwargs):
        """
        Retrieve the Operation query.

        :param object: Database connection.
        :param int:    User identifier.
        """
        return db.query(
            Operation
        ).join(
            User,
            User.id == Operation.user_id
        ).filter(
            Operation.user_id == user_id
        )
