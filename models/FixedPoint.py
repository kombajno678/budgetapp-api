from app import db, ma
from datetime import datetime


class FixedPoint(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow)

    when = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    exact_value = db.Column(db.Float, nullable=False)

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
