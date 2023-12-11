"""add initial_ball to game_players

Revision ID: be884a1d933c
Revises: 169b451d6f2d
Create Date: 2023-11-30 04:12:20.991534

"""
import sqlalchemy as sa
from alembic import op


revision = "be884a1d933c"
down_revision = "169b451d6f2d"


def upgrade():
    op.add_column(
        "game_players",
        sa.Column("initial_ball", sa.String(length=1), nullable=False),
    )


def downgrade():
    op.drop_column("game_players", "initial_ball")
