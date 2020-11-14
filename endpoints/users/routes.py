#from app import api
from ..routes import api
from .api import UserApi
from .operations import routes

api.add_resource(
    UserApi,
    "/users/<int:id>",
    "/users/",
    "/users"
)
