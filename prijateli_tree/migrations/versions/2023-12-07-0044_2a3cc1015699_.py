"""make game_player.created_game non nullable

Revision ID: 2a3cc1015699
Revises: 4e9a240059e0
Create Date: 2023-12-07 00:44:56.124938

"""
import sqlalchemy as sa
from alembic import op


revision = "2a3cc1015699"
down_revision = "4e9a240059e0"


def upgrade():
    op.alter_column(
        "game_players",
        "completed_game",
        existing_type=sa.BOOLEAN(),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "game_players",
        "completed_game",
        existing_type=sa.BOOLEAN(),
        nullable=True,
    )
