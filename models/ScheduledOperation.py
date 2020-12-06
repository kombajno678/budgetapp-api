from models.BaseModel import BaseModel
from app import db, ma
from datetime import datetime


class ScheduledOperation(BaseModel):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow)
    value = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100))

    schedule_id = db.Column(db.Integer, db.ForeignKey(
        'schedule.id'), nullable=False)

    schedule = db.relationship('Schedule', foreign_keys=schedule_id)

    active = db.Column(db.Boolean, nullable=False, default=True)

    hidden = db.Column(db.Boolean, nullable=False, default=False)

    category_id = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullable=True)

    category = db.relationship('Category', foreign_keys=category_id)

    cv = None
    n = None

    _default_fields = [
        "id",
        "user_id",
        "timestamp",
        "value",
        "schedule_id",
        "schedule",
        "active",
        "hidden",
        "category_id",
        "category"
    ]
    _hidden_fields = [
        "timestamp",
    ]
    _readonly_fields = [
        "id",
        "user_id",
        "timestamp",
    ]

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
