from ..api import RootApi
from models.User import User


class UserApi(RootApi):

    MODEL_CLASS = User
    '''
    def model_query(self, db, **kwargs):
       
        return db.query(
            User
        )
    '''
