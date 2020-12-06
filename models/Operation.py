from app import db, ma
from datetime import datetime
from sqlathanor import declarative_base, Column, relationship
from sqlalchemy import Integer, Float, Boolean, String, DateTime, ForeignKey
BaseModel = declarative_base()


class Operation(BaseModel):
    __tablename__ = 'operation'

    id = Column(db.Integer, primary_key=True, supports_json=True)
    user_id = Column(db.Integer, db.ForeignKey('user.id'),
                     nullable=False, supports_json=True)
    timestamp = Column(db.DateTime,
                       default=datetime.utcnow,
                       onupdate=datetime.utcnow, supports_json=True)
    value = Column(db.Float, nullable=False, supports_json=True)
    name = Column(db.String(100), supports_json=True)

    scheduled_operation_id = Column(
        db.Integer, db.ForeignKey('scheduled_operation.id'), nullable=True, supports_json=True)

    scheduled_operation = relationship(
        'scheduled_operation', foreign_keys=scheduled_operation_id, supports_json=True)

    when = Column(db.DateTime,
                  default=datetime.utcnow,
                  nullable=False, supports_json=True)

    category_id = Column(
        db.Integer, db.ForeignKey('category.id'), nullable=True, supports_json=True)

    category = relationship(
        'category', foreign_keys=category_id, supports_json=True)

    analyzed = False
    skipped = False

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
