"""result data field

Revision ID: f54a4434a8c8
Revises: 000000000000
Create Date: 2024-06-18 20:56:58.844367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f54a4434a8c8'
down_revision = '000000000000'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data', sa.JSON(), nullable=False))
        batch_op.drop_column('objects_count')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('result', schema=None) as batch_op:
        batch_op.drop_column('data')
        batch_op.add_column(sa.Column('objects_count', sa.INTEGER(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
