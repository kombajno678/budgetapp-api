from models.ScheduledOperation import ScheduledOperation
from models.User import User
from ...api import RootApi


class ScheduledOperationApi(RootApi):

    MODEL_CLASS = ScheduledOperation

    def model_query(self, user_id, **kwargs):
        if kwargs.get('id'):
            return ScheduledOperation.query.join(
                User,
                User.id == ScheduledOperation.user_id
            ).filter(
                ScheduledOperation.user_id == user_id,
                ScheduledOperation.id == kwargs.get('id')
            )
        else:
            return ScheduledOperation.query.join(
                User,
                User.id == ScheduledOperation.user_id
            ).filter(
                ScheduledOperation.user_id == user_id
            )
