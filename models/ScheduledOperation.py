from app import db, ma
from datetime import datetime


class ScheduledOperation(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey(
        'schedule.id'), nullable=False)

    value = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            print("ScheduledOperation init, %s == %s" % (key, value))
            setattr(self, key, value)

    def __repr__(self):
        return '<ScheduledOperation '+str(self.id)+' ' + str(self.schedule_id) + ' ' + str(self.value) + ' ' + str(self.name) + ' >'

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'user_id', 'timestamp', 'schedule_id',
                      'value', 'name')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
