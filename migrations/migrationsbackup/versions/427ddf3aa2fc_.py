"""empty message

Revision ID: 427ddf3aa2fc
Revises: 15a90ae9ccab
Create Date: 2014-11-24 11:05:41.805000

"""

# revision identifiers, used by Alembic.
revision = '427ddf3aa2fc'
down_revision = '15a90ae9ccab'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    ### end Alembic commands ###