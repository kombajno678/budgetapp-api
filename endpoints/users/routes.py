#from app import api
from ..routes import api
from .api import UserApi
from .operations import routes
from .schedules import routes
from .scheduledOperations import routes
from .fixedPoints import routes
from .categories import routes

api.add_resource(
    UserApi,
    "/users/<int:id>",
    "/users/",
    "/users"
)
