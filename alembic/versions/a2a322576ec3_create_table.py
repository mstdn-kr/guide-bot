"""create table

Revision ID: a2a322576ec3
Revises: 
Create Date: 2018-08-17 23:21:07.293752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2a322576ec3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'accounts',
        sa.Column('acct', sa.String(140), primary_key=True),
    )


def downgrade():
    op.drop_table('accounts')
