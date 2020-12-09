"""add schedule fields to sop

Revision ID: 9f6fcc77e5c6
Revises: 93aaa4aa4f53
Create Date: 2020-12-08 21:40:21.611305

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9f6fcc77e5c6'
down_revision = '93aaa4aa4f53'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('scheduled_operation',
                  sa.Column('year', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))
    op.add_column('scheduled_operation',
                  sa.Column('month', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))
    op.add_column('scheduled_operation',
                  sa.Column('day_of_month', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))
    op.add_column('scheduled_operation',
                  sa.Column('day_of_week', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))


def downgrade():
    op.drop_column('operation', 'year')
    op.drop_column('operation', 'year')
    op.drop_column('operation', 'month')
    op.drop_column('operation', 'day_of_month')
    op.drop_column('operation', 'day_of_week')
