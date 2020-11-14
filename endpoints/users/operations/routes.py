from ...routes import api
from .api import OperationApi

api.add_resource(
    OperationApi,
    "/users/<int:user_id>/operations/<int:id>",
    "/users/<int:user_id>/operations"
)
