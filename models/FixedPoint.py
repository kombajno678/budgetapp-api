from app import db, ma
from datetime import datetime
from sqlathanor import declarative_base, Column, relationship
from sqlalchemy import Integer, Float, Boolean, String, DateTime, ForeignKey
BaseModel = declarative_base()


class FixedPoint(BaseModel):
    __tablename__ = 'fixed_point'

    id = Column(db.Integer, primary_key=True, supports_json=True)

    user_id = Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False, supports_json=True)

    timestamp = Column(db.DateTime,
                       default=datetime.utcnow,
                       onupdate=datetime.utcnow, supports_json=True)

    when = Column(db.DateTime, default=datetime.utcnow,
                  nullable=False, supports_json=True)
    exact_value = Column(db.Float, nullable=False, supports_json=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            print("FixedPoint init, %s == %s" % (key, value))
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return '<FixedPoint '+str(self.id)+' ' + str(self.timestamp) + ' ' + str(self.when) + ' ' + str(self.exact_value) + '>'

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'user_id', 'timestamp', 'exact_value', 'when')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
