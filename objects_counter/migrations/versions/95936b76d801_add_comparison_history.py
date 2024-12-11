"""Add comparison history

Revision ID: 95936b76d801
Revises: 0c4a24df2108
Create Date: 2024-11-27 11:27:49.908606

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '95936b76d801'
down_revision = '0c4a24df2108'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('comparison',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('dataset_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('diff', sa.JSON(), nullable=False),
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['dataset_id'], ['dataset.id'], "fk_comparison_dataset_id_dataset"),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], "fk_comparison_user_id_user"),
                    sa.PrimaryKeyConstraint('id')
                    )
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comparison_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_image_comparison_id_comparison', 'comparison', ['comparison_id'], ['id'])


def downgrade():
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.drop_constraint('fk_image_comparison_id_comparison', type_='foreignkey')
        batch_op.drop_column('comparison_id')

    op.drop_table('comparison')
