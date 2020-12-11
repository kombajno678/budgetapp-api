from ...routes import api
from .api import CategoryApi

api.add_resource(
    CategoryApi,
    "/users/<int:path_user_id>/categories/<int:id>",
    "/users/<int:path_user_id>/categories"
)
