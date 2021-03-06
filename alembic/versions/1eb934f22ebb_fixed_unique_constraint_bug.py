"""Fixed UNIQUE constraint bug

Revision ID: 1eb934f22ebb
Revises: 
Create Date: 2015-02-26 01:39:12.835088

"""

# revision identifiers, used by Alembic.
revision = '1eb934f22ebb'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_name', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_name')
    )
    op.create_table('permissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('permission_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('permission_name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('middle_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('active_role', sa.String(length=255), nullable=True),
    sa.Column('supervisor', sa.String(length=255), nullable=True),
    sa.Column('is_supervisor', sa.Boolean(), nullable=True),
    sa.Column('supervisee', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('hours', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hours')
    )
    op.create_table('role_perms',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    op.create_table('userstatistics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('proposed_offset', sa.Integer(), nullable=True),
    sa.Column('vl', sa.Integer(), nullable=True),
    sa.Column('vlDates', sa.PickleType(), nullable=True),
    sa.Column('vlDatesRecord', sa.PickleType(), nullable=True),
    sa.Column('vlDatesCancelled', sa.PickleType(), nullable=True),
    sa.Column('vlDatesConfirmedCancelled', sa.PickleType(), nullable=True),
    sa.Column('vlDatesAppliedDates', sa.PickleType(), nullable=True),
    sa.Column('vlDatesDecidedDates', sa.PickleType(), nullable=True),
    sa.Column('sl', sa.Integer(), nullable=True),
    sa.Column('slDates', sa.PickleType(), nullable=True),
    sa.Column('slDatesRecord', sa.PickleType(), nullable=True),
    sa.Column('slDatesCancelled', sa.PickleType(), nullable=True),
    sa.Column('slDatesConfirmedCancelled', sa.PickleType(), nullable=True),
    sa.Column('slDatesAppliedDates', sa.PickleType(), nullable=True),
    sa.Column('slDatesDecidedDates', sa.PickleType(), nullable=True),
    sa.Column('offset', sa.Integer(), nullable=True),
    sa.Column('offsetDates', sa.PickleType(), nullable=True),
    sa.Column('offsetDatesRecord', sa.PickleType(), nullable=True),
    sa.Column('offestDatesCancelled', sa.PickleType(), nullable=True),
    sa.Column('offestDatesConfirmedCancelled', sa.PickleType(), nullable=True),
    sa.Column('offsetDatesAppliedDates', sa.PickleType(), nullable=True),
    sa.Column('offsetDatesDecidedDates', sa.PickleType(), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Payslip',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('user', sa.Integer(), nullable=True),
    sa.Column('filename', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Payslip_date'), 'Payslip', ['date'], unique=False)
    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_table('user_projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], [u'projects.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('profileImages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Integer(), nullable=True),
    sa.Column('image', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profileImages')
    op.drop_table('user_projects')
    op.drop_table('user_roles')
    op.drop_index(op.f('ix_Payslip_date'), table_name='Payslip')
    op.drop_table('Payslip')
    op.drop_table('userstatistics')
    op.drop_table('role_perms')
    op.drop_table('logs')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('permissions')
    op.drop_table('projects')
    ### end Alembic commands ###
