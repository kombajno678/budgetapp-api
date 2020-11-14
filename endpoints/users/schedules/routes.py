from ...routes import api
from .api import ScheduleApi

api.add_resource(
    ScheduleApi,
    "/users/<int:path_user_id>/schedules/<int:id>",
    "/users/<int:path_user_id>/schedules"
)
