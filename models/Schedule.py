from app import db, ma
from datetime import datetime
from sqlathanor import declarative_base, Column, relationship
from sqlalchemy import Integer, Float, Boolean, String, DateTime, ForeignKey
BaseModel = declarative_base()


class Schedule(BaseModel):
    __tablename__ = 'schedule'

    id = Column(db.Integer, primary_key=True, supports_json=True)

    user_id = Column(db.Integer, db.ForeignKey('user.id'),
                     nullable=False, supports_json=True)
    timestamp = Column(db.DateTime,
                       default=datetime.utcnow,
                       onupdate=datetime.utcnow, supports_json=True)
    year = Column(db.ARRAY(db.Integer), nullable=True, supports_json=True)
    month = Column(db.ARRAY(db.Integer), nullable=True, supports_json=True)
    day_of_month = Column(db.ARRAY(db.Integer),
                          nullable=True, supports_json=True)
    day_of_week = Column(db.ARRAY(db.Integer),
                         nullable=True, supports_json=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            #print("Schedule init, %s == %s" % (key, value))
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return '<Schedule '+str(self.id)+' ' + str(self.year) + ' ' + str(self.month) + ' ' + str(self.day_of_month) + ' ' + str(self.day_of_week) + ' ' + ' >'

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'user_id', 'timestamp', 'year',
                      'month', 'day_of_month', 'day_of_week')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
