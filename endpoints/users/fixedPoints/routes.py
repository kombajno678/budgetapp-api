from ...routes import api
from .api import FixedPointApi

api.add_resource(
    FixedPointApi,
    "/users/<int:path_user_id>/fixed_points/<int:id>",
    "/users/<int:path_user_id>/fixed_points"
)
