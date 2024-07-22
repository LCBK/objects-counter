"""empty message

Revision ID: b8460c7ba591
Revises: f54a4434a8c8
Create Date: 2024-07-22 20:35:12.214645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8460c7ba591'
down_revision = 'f54a4434a8c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.add_column(sa.Column('background_points', sa.JSON(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint('constr_user_username', ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('constr_user_username', type_='unique')

    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.drop_column('background_points')

    # ### end Alembic commands ###
