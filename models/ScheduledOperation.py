from app import db, ma
from datetime import datetime


class ScheduledOperation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow)
    value = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100))

    schedule_id = db.Column(db.Integer, db.ForeignKey(
        'schedule.id'), nullable=False)

    active = db.Column(db.Boolean, nullable=False, default=True)

    hidden = db.Column(db.Boolean, nullable=False, default=False)

    category_id = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullable=True)

    category = db.relationship('Category', foreign_keys=category_id)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            #print("ScheduledOperation init, %s == %s" % (key, value))
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return '<ScheduledOperation '+str(self.id)+' ' + str(self.schedule_id) + ' ' + str(self.value) + ' ' + str(self.name) + ' >'

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'user_id', 'timestamp', 'schedule_id',
                      'value', 'name', 'active', 'hidden', 'category_id')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
