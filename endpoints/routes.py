from app import api
from .users import routes
from .api import RootApi

print('INIT-root-api-routes: api.add_resource')
api.add_resource(RootApi, '/api', '/api/', endpoint='api')
