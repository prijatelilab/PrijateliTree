"""empty message

Revision ID: 2904026841be
Revises: 3d92f1e628d4
Create Date: 2023-11-25 04:43:26.435386

"""
import sqlalchemy as sa
from alembic import op


revision = "2904026841be"
down_revision = "3d92f1e628d4"


def upgrade():
    op.create_table(
        "game_sessions",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, cycle=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "num_games",
            sa.Integer(),
            server_default=sa.text("16"),
            nullable=False,
        ),
        sa.Column(
            "finished",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="users_created_by_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "session_players",
        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False, start=1, cycle=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column(
            "ready",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "points", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "correct_answers",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="users_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["game_sessions.id"],
            name="session_players_session_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="session_players_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "denirs",
        sa.Column("created_by_session_id", sa.Integer(), nullable=True),
    )
    op.drop_constraint(
        "denirs_created_by_game_id_fkey", "denirs", type_="foreignkey"
    )
    op.create_foreign_key(
        "denirs_created_by_session_id_fkey",
        "denirs",
        "game_sessions",
        ["created_by_session_id"],
        ["id"],
    )
    op.drop_column("denirs", "created_by_game_id")
    op.add_column(
        "game_players",
        sa.Column("session_player_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        "session_players_player_id_fkey",
        "game_players",
        "session_players",
        ["session_player_id"],
        ["id"],
    )
    op.add_column(
        "games", sa.Column("game_session_id", sa.Integer(), nullable=False)
    )
    op.create_foreign_key(
        "games_game_session_id_fkey",
        "games",
        "game_sessions",
        ["game_session_id"],
        ["id"],
    )
    op.add_column(
        "player_survey_answers",
        sa.Column("session_player_id", sa.Integer(), nullable=False),
    )
    op.drop_constraint(
        "uix_session_answer", "player_survey_answers", type_="unique"
    )
    op.create_unique_constraint(
        "uix_session_survey_answer",
        "player_survey_answers",
        ["session_player_id", "survey_id"],
    )
    op.drop_constraint(
        "player_survey_answers_player_id_fkey",
        "player_survey_answers",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "player_survey_answers_session_player_id_fkey",
        "player_survey_answers",
        "session_players",
        ["session_player_id"],
        ["id"],
    )
    op.drop_column("player_survey_answers", "player_id")


def downgrade():
    op.add_column(
        "player_survey_answers",
        sa.Column(
            "player_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.drop_constraint(
        "player_survey_answers_session_player_id_fkey",
        "player_survey_answers",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "player_survey_answers_player_id_fkey",
        "player_survey_answers",
        "game_players",
        ["player_id"],
        ["id"],
    )
    op.drop_constraint(
        "uix_session_survey_answer", "player_survey_answers", type_="unique"
    )
    op.create_unique_constraint(
        "uix_session_answer",
        "player_survey_answers",
        ["player_id", "survey_id"],
    )
    op.drop_column("player_survey_answers", "session_player_id")
    op.drop_constraint(
        "games_game_session_id_fkey", "games", type_="foreignkey"
    )
    op.drop_column("games", "game_session_id")
    op.drop_constraint(
        "session_players_player_id_fkey", "game_players", type_="foreignkey"
    )
    op.drop_column("game_players", "session_player_id")
    op.add_column(
        "denirs",
        sa.Column(
            "created_by_game_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(
        "denirs_created_by_session_id_fkey", "denirs", type_="foreignkey"
    )
    op.create_foreign_key(
        "denirs_created_by_game_id_fkey",
        "denirs",
        "games",
        ["created_by_game_id"],
        ["id"],
    )
    op.drop_column("denirs", "created_by_session_id")
    op.drop_table("session_players")
    op.drop_table("game_sessions")
