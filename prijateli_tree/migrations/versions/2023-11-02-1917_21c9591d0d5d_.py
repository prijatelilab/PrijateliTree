"""empty message

Revision ID: 21c9591d0d5d
Revises: 5489fb45e45e
Create Date: 2023-11-02 19:17:52.387308

"""
import sqlalchemy as sa
from alembic import op


revision = "21c9591d0d5d"
down_revision = "5489fb45e45e"


def upgrade():
    op.add_column(
        "game_players", sa.Column("ready", sa.Boolean(), nullable=False)
    )


def downgrade():
    op.drop_column("game_players", "ready")
