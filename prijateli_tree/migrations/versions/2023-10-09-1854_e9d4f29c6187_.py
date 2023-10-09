"""empty message

Revision ID: e9d4f29c6187
Revises: e5b498dd07a6
Create Date: 2023-10-09 18:54:41.255924

"""
import sqlalchemy as sa
from alembic import op


revision = "e9d4f29c6187"
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
    op.add_column(
        "player_survey_answers", sa.Column("session_id", sa.Integer(), nullable=False)
    )
    op.create_unique_constraint(
        "uix_session_answer",
        "player_survey_answers",
        ["player_id", "survey_id", "session_id"],
    )
    op.create_foreign_key(
        "player_survey_answers_session_id_fkey",
        "player_survey_answers",
        "sessions",
        ["session_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "player_survey_answers_session_id_fkey",
        "player_survey_answers",
        type_="foreignkey",
    )
    op.drop_constraint("uix_session_answer", "player_survey_answers", type_="unique")
    op.drop_column("player_survey_answers", "session_id")
    op.drop_column("player_survey_answers", "id")
    op.create_primary_key(
        "player_survey_answers_pkey",
        "player_survey_answers",
        ["player_id", "survey_id"],
    )
