"""empty message

Revision ID: 260d503a3c0d
Revises: e5b498dd07a6
Create Date: 2023-10-09 19:37:42.103853

"""
import sqlalchemy as sa
from alembic import op


revision = "260d503a3c0d"
down_revision = "e5b498dd07a6"


def upgrade():
    op.execute(
        """
        ALTER TABLE player_survey_answers
        DROP CONSTRAINT player_survey_answers_pkey;
    """
    )
    op.add_column(
        "player_survey_answers",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, cycle=True),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uix_session_answer",
        "player_survey_answers",
        ["player_id", "survey_id"],
    )
    op.drop_constraint(
        "player_survey_answers_player_id_fkey",
        "player_survey_answers",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "player_survey_answers_player_id_fkey",
        "player_survey_answers",
        "session_players",
        ["player_id"],
        ["id"],
    )
    op.add_column(
        "session_players", sa.Column("user_id", sa.Integer(), nullable=False)
    )
    op.drop_constraint(
        "session_players_player_id_fkey", "session_players", type_="foreignkey"
    )
    op.create_foreign_key(
        "session_players_player_id_fkey",
        "session_players",
        "users",
        ["user_id"],
        ["id"],
    )
    op.drop_column("session_players", "player_id")


def downgrade():
    op.add_column(
        "session_players",
        sa.Column(
            "player_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(
        "session_players_player_id_fkey", "session_players", type_="foreignkey"
    )
    op.create_foreign_key(
        "session_players_player_id_fkey",
        "session_players",
        "users",
        ["player_id"],
        ["id"],
    )
    op.drop_column("session_players", "user_id")
    op.drop_constraint(
        "player_survey_answers_player_id_fkey",
        "player_survey_answers",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "player_survey_answers_player_id_fkey",
        "player_survey_answers",
        "users",
        ["player_id"],
        ["id"],
    )
    op.drop_constraint(
        "uix_session_answer", "player_survey_answers", type_="unique"
    )
    op.drop_column("player_survey_answers", "id")
    op.create_primary_key(
        "player_survey_answers_pkey",
        "player_survey_answers",
        ["player_id", "survey_id"],
    )
