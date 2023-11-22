"""empty message

Revision ID: 3d92f1e628d4
Revises: 8d6d2f92cb84
Create Date: 2023-11-22 23:51:01.079824

"""
from alembic import op


revision = "3d92f1e628d4"
down_revision = "8d6d2f92cb84"


def upgrade():
    op.create_unique_constraint(
        "game_player_id_round_key", "game_answers", ["game_player_id", "round"]
    )


def downgrade():
    op.drop_constraint(
        "game_player_id_round_key", "game_answers", type_="unique"
    )
