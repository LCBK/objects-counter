"""handle deleting dataset in history

Revision ID: f6a92057073f
Revises: da3918d0dcb4
Create Date: 2024-12-11 20:48:51.532052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6a92057073f'
down_revision = 'da3918d0dcb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comparison', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comparison_dataset_id_dataset', type_='foreignkey')
        batch_op.create_foreign_key('fk_comparison_dataset_id_dataset', 'dataset', ['dataset_id'], ['id'],
                                    ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comparison', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comparison_dataset_id_dataset', type_='foreignkey')
        batch_op.create_foreign_key('fk_comparison_dataset_id_dataset', 'dataset', ['dataset_id'], ['id'])

    # ### end Alembic commands ###