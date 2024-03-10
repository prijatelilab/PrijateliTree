"""add session_key (nullable)

Revision ID: 4779983a5948
Revises: 68e551f35b21
Create Date: 2024-03-10 17:44:27.091544

"""
from alembic import op
import sqlalchemy as sa



revision = '4779983a5948'
down_revision = '68e551f35b21'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_sessions', sa.Column('session_key', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game_sessions', 'session_key')
    # ### end Alembic commands ###
