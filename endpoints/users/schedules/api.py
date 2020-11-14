from models.Schedule import Schedule
from models.User import User
from ...api import RootApi


class ScheduleApi(RootApi):

    MODEL_CLASS = Schedule

    def model_query(self, db, user_id, **kwargs):
        if kwargs.get('id'):
            return Schedule.query.join(
                User,
                User.id == Schedule.user_id
            ).filter(
                Schedule.user_id == user_id,
                Schedule.id == kwargs.get('id')
            )
        else:
            return Schedule.query.join(
                User,
                User.id == Schedule.user_id
            ).filter(
                Schedule.user_id == user_id
            )
