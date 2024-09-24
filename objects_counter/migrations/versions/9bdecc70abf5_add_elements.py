"""Add ImageElement table

Revision ID: 9bdecc70abf5
Revises: b8460c7ba591
Create Date: 2024-09-16 21:32:34.528269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bdecc70abf5'
down_revision = 'b8460c7ba591'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('image_element',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('image_id', sa.Integer(), nullable=False),
    sa.Column('top_left', sa.JSON(), nullable=False),
    sa.Column('bottom_right', sa.JSON(), nullable=False),
    sa.Column('classification', sa.String(length=255), nullable=True),
    sa.Column('certainty', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('image_element')
