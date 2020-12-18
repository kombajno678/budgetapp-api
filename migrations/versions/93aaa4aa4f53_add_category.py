"""add category

Revision ID: 93aaa4aa4f53
Revises: 687b10756a75
Create Date: 2020-12-04 09:51:53.323887

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '93aaa4aa4f53'
down_revision = '687b10756a75'
branch_labels = None
depends_on = None


def upgrade():
    #op.drop_column('scheduled_operation', 'category_id')
    #op.drop_column('operation', 'category_id')
    # op.drop_table('category')

    op.create_table('category',
                    sa.Column('id', sa.INTEGER(),
                              autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.INTEGER(),
                              autoincrement=False, nullable=True),
                    sa.Column('timestamp', postgresql.TIMESTAMP(),
                              autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=100),
                              autoincrement=False, nullable=True),
                    sa.Column('icon', sa.VARCHAR(length=100),
                              autoincrement=False, nullable=True),
                    sa.Column('color', sa.VARCHAR(length=100),
                              autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(
                        ['user_id'], ['user.id'], name='category_user_id_fkey'),
                    sa.PrimaryKeyConstraint('id', name='category_pkey')
                    )

    op.add_column('scheduled_operation',
                  sa.Column('category_id', sa.INTEGER,
                            sa.ForeignKey('category.id'))
                  )
    op.add_column('operation',
                  sa.Column('category_id', sa.INTEGER,
                            sa.ForeignKey('category.id'))
                  )

    '''
    op.add_column('scheduled_operation', 'category_id',
                  sa.ForeignKeyConstraint(
                      ['category_id'], ['category.id'], name='scheduled_operation_category_id_fkey')
                  )

    op.add_column('operation', 'category_id',
                  sa.ForeignKeyConstraint(
                      ['category_id'], ['category.id'], name='operation_category_id_fkey')
                  )
    '''


def downgrade():
    op.drop_column('scheduled_operation', 'category_id')
    op.drop_column('operation', 'category_id')
    op.drop_table('category')

    # ### end Alembic commands ###
