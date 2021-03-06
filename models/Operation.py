from models.BaseModel import BaseModel
from app import db, ma
from datetime import datetime


class Operation(BaseModel):
    __tablename__ = "operation"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          onupdate=datetime.utcnow)
    value = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100))

    scheduled_operation_id = db.Column(
        db.Integer, db.ForeignKey('scheduled_operation.id'), nullable=True)

    scheduled_operation = db.relationship(
        'ScheduledOperation', foreign_keys=scheduled_operation_id)

    when = db.Column(db.DateTime,
                     default=datetime.utcnow,
                     nullable=False)

    category_id = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullable=True)

    category = db.relationship('Category', foreign_keys=category_id)

    analyzed = False
    skipped = False

    _default_fields = [
        "id",
        "user_id",
        "timestamp",
        "value",
        "name",
        "scheduled_operation_id",
        "scheduled_operation",
        "when",
        "category_id",
        "category",
    ]

    # _hidden_fields = [
    #     "timestamp",
    # ]
    _readonly_fields = [
        "id",
        "user_id",
        "timestamp",
    ]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            #print("Operation init, %s == %s" % (key, value))
            if hasattr(self, key):
                setattr(self, key, value)

        '''
        self.user_id = kwargs.get('user_id', None)
        self.scheduled_operation_id = kwargs.get('scheduled_operation_id', None)
        self.value = kwargs.get('value', None)
        self.name = kwargs.get('name', None)
        '''

    def __repr__(self):
        return '<Operation id='+str(self.id)+' value=' + str(self.value) + ' name=' + self.name + ' when=' + str(self.when) + '>'

    class Schema(ma.Schema):
        class Meta:
            fields = ('id', 'user_id', 'scheduled_operation_id',
                      'when', 'timestamp', 'value', 'name', 'category_id')

    # init schema
    schema = Schema()
    schemas = Schema(many=True)
