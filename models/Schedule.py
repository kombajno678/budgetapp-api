from app import db, ma
from datetime import datetime


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow)
    year = db.Column(db.ARRAY(db.Integer), nullable=True)
    month = db.Column(db.ARRAY(db.Integer), nullable=True)
    day_of_month = db.Column(db.ARRAY(db.Integer), nullable=True)
    day_of_week = db.Column(db.ARRAY(db.Integer), nullable=True)

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
