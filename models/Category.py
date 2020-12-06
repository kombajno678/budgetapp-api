from app import db, ma
from datetime import datetime
from sqlathanor import declarative_base, Column, relationship
from sqlalchemy import Integer, Float, Boolean, String, DateTime, ForeignKey
BaseModel = declarative_base()


class Category(BaseModel):
    __tablename__ = 'category'

    id = Column(db.Integer, primary_key=True, supports_json=True)
    user_id = Column(db.Integer, db.ForeignKey('user.id'),
                     nullable=True, supports_json=True)
    timestamp = Column(db.DateTime,
                       default=datetime.utcnow,
                       onupdate=datetime.utcnow, supports_json=True)

    name = Column(db.String(100), supports_json=True)
    icon = Column(db.String(100), supports_json=True)
    color = Column(db.String(100), supports_json=True)

    analyzed = False

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
