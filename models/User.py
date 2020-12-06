from app import db, ma
from datetime import datetime
from sqlathanor import declarative_base, Column, relationship
from sqlalchemy import Integer, Float, Boolean, String, DateTime, ForeignKey
BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = 'user'

    id = Column(db.Integer, primary_key=True, supports_json=True)

    created = Column(db.DateTime,
                     default=datetime.utcnow, supports_json=True)

    # when were operations generated last time (from scheduled operations)
    last_generated_operations_at = Column(
        db.DateTime, nullable=True, supports_json=True)

    # user id from auth0
    auth_id = Column(db.String(100), unique=True,
                     nullable=False, supports_json=True)
    '''
    # operations
    operations = relationship(
        'operation', backref=db.backref('user', lazy='joined'), lazy=True, supports_json=True)

    # scheduledOperations
    scheduledOperations = relationship(
        'scheduled_operation', backref=db.backref('user', lazy='joined'), lazy=True, supports_json=True)

    # schedules
    schedules = relationship(
        'schedule', backref=db.backref('user', lazy='joined'), lazy=True, supports_json=True)
    '''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            #print("User init, %s == %s" % (key, value))
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
            fields = ('id', 'auth_id', 'created',
                      'last_generated_operations_at')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
