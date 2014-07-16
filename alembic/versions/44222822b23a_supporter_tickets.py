"""supporter tickets

Revision ID: 44222822b23a
Revises: 20a901f9c82c
Create Date: 2014-07-15 14:40:46.143494

"""

# revision identifiers, used by Alembic.
revision = '44222822b23a'
down_revision = '20a901f9c82c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tickets', sa.Column('support', sa.Float(), nullable=True))
    op.add_column('tickets', sa.Column('ticket_support', sa.Boolean(), nullable=True))
    op.add_column('tickets', sa.Column('ticket_support_x', sa.Boolean(), nullable=True))
    op.add_column('tickets', sa.Column('ticket_support_xl', sa.Boolean(), nullable=True))
    #op.drop_column('tickets', 'ticket_type')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.add_column('tickets', sa.Column('ticket_type', sa.INTEGER(), nullable=True))
    op.drop_column('tickets', 'ticket_support_xl')
    op.drop_column('tickets', 'ticket_support_x')
    op.drop_column('tickets', 'ticket_support')
    op.drop_column('tickets', 'support')
    ### end Alembic commands ###
