from app import db, ma
from datetime import datetime


class Category(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow)

    name = db.Column(db.String(100))
    icon = db.Column(db.String(100))
    color = db.Column(db.String(100))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return '<Category '+str(self.id)+' '+str(self.user_id)+' ' + str(self.name) + '>'

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'user_id', 'timestamp',
                      'name', 'icon', 'color')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
