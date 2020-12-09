"""delete schedule fk from sop

Revision ID: a49b98089f9f
Revises: 9f6fcc77e5c6
Create Date: 2020-12-09 00:18:06.609820

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a49b98089f9f'
down_revision = '9f6fcc77e5c6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('scheduled_operation', 'schedule_id')


def downgrade():
    op.add_column('scheduled_operation',
                  sa.Column('schedule_id', sa.INTEGER(), autoincrement=False, nullable=False))
