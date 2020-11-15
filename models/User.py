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

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            print("User init, %s == %s" % (key, value))
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return '<User %r>' % self.auth_id

    def getByAuthId(auth_id):
        # if user exists, return
        existing_user = User.query.filter_by(auth_id=auth_id).first()
        if existing_user is not None:
            return existing_user
        else:
            # else, create new user objcet
            new_user = User()
            new_user.auth_id = auth_id
            db.session.add(new_user)
            try:
                db.session.commit()
                return new_user
            except Exception as err:
                print(err)
                return None

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'auth_id', 'created')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
