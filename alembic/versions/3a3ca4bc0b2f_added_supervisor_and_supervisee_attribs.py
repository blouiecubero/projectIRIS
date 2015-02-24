"""Added supervisor and supervisee attribs

Revision ID: 3a3ca4bc0b2f
Revises: 95bdd880210
Create Date: 2015-02-12 11:18:27.367000

"""

# revision identifiers, used by Alembic.
revision = '3a3ca4bc0b2f'
down_revision = '95bdd880210'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_supervisor', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('supervisee', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('supervisor', sa.String(length=255), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'supervisor')
    op.drop_column('users', 'supervisee')
    op.drop_column('users', 'is_supervisor')
    ### end Alembic commands ###
