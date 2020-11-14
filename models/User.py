from app import db, ma
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime,
                        default=datetime.utcnow)

    # user id from auth0
    auth_id = db.Column(db.String(100), unique=True, nullable=False)

    # operations
    operations = db.relationship(
        'Operation', backref=db.backref('user', lazy='joined'), lazy=True)

    # scheduledOperations
    scheduledOperations = db.relationship(
        'ScheduledOperation', backref=db.backref('user', lazy='joined'), lazy=True)

    # schedules
    schedules = db.relationship(
        'Schedule', backref=db.backref('user', lazy='joined'), lazy=True)

    def __init__(self, auth_id):
        self.auth_id = auth_id

    def __repr__(self):
        return '<User %r>' % self.auth_id

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'auth_id', 'created')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
