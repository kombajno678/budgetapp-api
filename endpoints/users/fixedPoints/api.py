from models.FixedPoint import FixedPoint
from models.User import User
from ...api import RootApi


class FixedPointApi(RootApi):

    MODEL_CLASS = FixedPoint

    def model_query(self, db, user_id, **kwargs):

        if kwargs.get('id'):
            return FixedPoint.query.join(
                User,
                User.id == FixedPoint.user_id
            ).filter(
                FixedPoint.user_id == user_id,
                FixedPoint.id == kwargs.get('id')
            )
        else:
            return FixedPoint.query.join(
                User,
                User.id == FixedPoint.user_id
            ).filter(
                FixedPoint.user_id == user_id
            )
