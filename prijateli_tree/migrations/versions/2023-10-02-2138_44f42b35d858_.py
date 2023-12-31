"""empty message

Revision ID: 44f42b35d858
Revises:
Create Date: 2023-10-02 21:38:31.871571

"""
import sqlalchemy as sa
from alembic import op


revision = "44f42b35d858"
down_revision = None


def upgrade():
    op.create_table(
        "languages",
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
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("abbr", sa.String(length=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("abbr"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "session_types",
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
        sa.Column("network", sa.String(), nullable=False),
        sa.Column("bag", sa.String(), nullable=False),
        sa.CheckConstraint(
            "network in ('integrated', 'segregated', 'self-selected')",
            name="network_options",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("network"),
    )
    op.create_table(
        "users",
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
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("language_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "role in ('super-admin', 'admin', 'student')", name="role_options"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="users_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["language_id"], ["languages.id"], name="users_languages_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone_number"),
    )
    op.create_table(
        "sessions",
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
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("session_type_id", sa.Integer(), nullable=False),
        sa.Column("rounds", sa.Integer(), nullable=False),
        sa.Column("practice", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="sessions_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["session_type_id"],
            ["users.id"],
            name="sessions_session_type_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "surveys",
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
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="surveys_created_by_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "denirs",
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
        sa.Column("created_by_session_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "created_by_session_id IS NOT NULL OR created_by_user_id IS NOT NULL",
            name="created_by_check",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_session_id"],
            ["sessions.id"],
            name="denirs_created_by_session_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="denirs_created_by_user_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_table(
        "player_survey_answers",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("survey_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["player_id"],
            ["users.id"],
            name="player_survey_answers_player_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["survey_id"],
            ["surveys.id"],
            name="player_survey_answers_survey_id_fkey",
        ),
        sa.PrimaryKeyConstraint(
            "player_id", "survey_id", name="player_survey_answers_pkey"
        ),
    )
    op.create_table(
        "session_answers",
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
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("player_answer", sa.String(length=1), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["player_id"], ["users.id"], name="session_answers_player_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name="session_answers_session_id_fkey",
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
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("name_hidden", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="session_players_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["player_id"], ["users.id"], name="session_players_player_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name="session_players_session_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("session_players")
    op.drop_table("session_answers")
    op.drop_table("player_survey_answers")
    op.drop_table("denirs")
    op.drop_table("surveys")
    op.drop_table("sessions")
    op.drop_table("users")
    op.drop_table("session_types")
    op.drop_table("languages")
