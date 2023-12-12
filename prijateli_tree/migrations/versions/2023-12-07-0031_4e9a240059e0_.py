"""add completed_game flag to session_players

Revision ID: 4e9a240059e0
Revises: be884a1d933c
Create Date: 2023-12-07 00:31:27.078581

"""
import sqlalchemy as sa
from alembic import op


revision = "4e9a240059e0"
down_revision = "be884a1d933c"


def upgrade():
    op.add_column(
        "game_players", sa.Column("completed_game", sa.Boolean(), nullable=True)
    )


def downgrade():
    op.drop_column("game_players", "completed_game")
