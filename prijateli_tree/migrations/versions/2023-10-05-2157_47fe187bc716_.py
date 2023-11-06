"""empty message

Revision ID: 47fe187bc716
Revises: 44f42b35d858
Create Date: 2023-10-05 21:57:10.011419

"""
import sqlalchemy as sa
from alembic import op


revision = "47fe187bc716"
down_revision = "44f42b35d858"


def upgrade():
    op.add_column(
        "session_answers",
        sa.Column("session_player_id", sa.Integer(), nullable=False),
    )
    op.drop_constraint(
        "session_answers_session_id_fkey", "session_answers", type_="foreignkey"
    )
    op.drop_constraint(
        "session_answers_player_id_fkey", "session_answers", type_="foreignkey"
    )
    op.create_foreign_key(
        "session_answers_session_players_fkey",
        "session_answers",
        "session_players",
        ["session_player_id"],
        ["id"],
    )
    op.drop_column("session_answers", "player_id")
    op.drop_column("session_answers", "session_id")
    op.add_column(
        "session_players", sa.Column("position", sa.Integer(), nullable=False)
    )

    op.execute(
        """
            INSERT INTO session_types
            (network, bag)
            VALUES
            ('integrated', 'RRRRBB'),
            ('segregated', 'RRRRBB'),
            ('self-selected', 'RRRRBB')
        """
    )


def downgrade():
    op.drop_column("session_players", "position")
    op.add_column(
        "session_answers",
        sa.Column(
            "session_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "session_answers",
        sa.Column(
            "player_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(
        "session_answers_session_players_fkey",
        "session_answers",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "session_answers_player_id_fkey",
        "session_answers",
        "users",
        ["player_id"],
        ["id"],
    )
    op.create_foreign_key(
        "session_answers_session_id_fkey",
        "session_answers",
        "sessions",
        ["session_id"],
        ["id"],
    )
    op.drop_column("session_answers", "session_player_id")

    op.execute(
        """
            DELETE FROM session_types
            WHERE bag = 'RRRRBB';
        """
    )
