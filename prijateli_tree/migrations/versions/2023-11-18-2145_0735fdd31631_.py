"""empty message

Revision ID: 0735fdd31631
Revises: 30991d313ac8
Create Date: 2023-11-18 21:45:17.443658

"""
from alembic import op
import sqlalchemy as sa



revision = '0735fdd31631'
down_revision = '30991d313ac8'


def upgrade():
    op.add_column('games', sa.Column('next_game_id', sa.Integer(), nullable=True))
    op.create_foreign_key('games_next_game_id_fkey', 'games', 'games', ['next_game_id'], ['id'])


def downgrade():
    op.drop_constraint('games_next_game_id_fkey', 'games', type_='foreignkey')
    op.drop_column('games', 'next_game_id')
