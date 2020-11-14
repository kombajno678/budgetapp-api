from ...routes import api
from .api import ScheduledOperationApi

api.add_resource(
    ScheduledOperationApi,
    "/users/<int:path_user_id>/scheduled_operations/<int:id>",
    "/users/<int:path_user_id>/scheduled_operations"
)
