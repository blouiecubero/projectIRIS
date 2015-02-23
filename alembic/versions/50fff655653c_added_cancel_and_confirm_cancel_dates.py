"""Added cancel and confirm cancel dates

Revision ID: 50fff655653c
Revises: 2d2d6ca3b27b
Create Date: 2015-02-19 21:24:32.664000

"""

# revision identifiers, used by Alembic.
revision = '50fff655653c'
down_revision = '2d2d6ca3b27b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userstatistics', sa.Column('offestDatesConfirmedCancelled', sa.PickleType(), nullable=True))
    op.add_column('userstatistics', sa.Column('slDatesConfirmedCancelled', sa.PickleType(), nullable=True))
    op.add_column('userstatistics', sa.Column('vlDatesConfirmedCancelled', sa.PickleType(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('userstatistics', 'vlDatesConfirmedCancelled')
    op.drop_column('userstatistics', 'slDatesConfirmedCancelled')
    op.drop_column('userstatistics', 'offestDatesConfirmedCancelled')
    ### end Alembic commands ###