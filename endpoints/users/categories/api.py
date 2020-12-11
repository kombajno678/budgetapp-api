from models.Category import Category
from models.User import User
from ...api import RootApi


class CategoryApi(RootApi):

    MODEL_CLASS = Category

    def model_query(self, db, user_id, **kwargs):

        if kwargs.get('id'):
            return Category.query.join(
                User,
                User.id == Category.user_id
            ).filter(
                Category.user_id == user_id,
                Category.id == kwargs.get('id')
            )
        else:
            return Category.query.join(
                User,
                User.id == Category.user_id
            ).filter(
                Category.user_id == user_id
            )
