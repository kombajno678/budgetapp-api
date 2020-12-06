from app import db, ma
from datetime import datetime

from sqlathanor import declarative_base, Column, relationship
from sqlalchemy import Integer, Float, Boolean, String, DateTime, ForeignKey
BaseModel = declarative_base()


class ScheduledOperation(BaseModel):
    __tablename__ = 'scheduled_operation'

    id = Column(db.Integer, primary_key=True, supports_json=True)
    user_id = Column(db.Integer, db.ForeignKey('user.id'),
                     nullable=False, supports_json=True)
    timestamp = Column(db.DateTime,
                       default=datetime.utcnow,
                       onupdate=datetime.utcnow, supports_json=True)
    value = Column(db.Float, nullable=False, supports_json=True)
    name = Column(db.String(100), supports_json=True)

    schedule_id = Column(db.Integer, db.ForeignKey(
        'schedule.id'), nullable=False, supports_json=True)

    schedule = relationship(
        'schedule', foreign_keys=schedule_id, supports_json=True)

    active = Column(db.Boolean, nullable=False,
                    default=True, supports_json=True)

    hidden = Column(db.Boolean, nullable=False,
                    default=False, supports_json=True)

    category_id = Column(
        db.Integer, db.ForeignKey('category.id'), nullable=True, supports_json=True)

    category = relationship(
        'category', foreign_keys=category_id, supports_json=True)

    cv = None
    n = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            #print("ScheduledOperation init, %s == %s" % (key, value))
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f"<ScheduledOp: {self.id} {self.value:8.2f} {self.name[0:35]} (cv={self.cv:.2f}; n={self.n})>"

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'user_id', 'timestamp', 'schedule_id',
                      'value', 'name', 'active', 'hidden', 'category_id')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
