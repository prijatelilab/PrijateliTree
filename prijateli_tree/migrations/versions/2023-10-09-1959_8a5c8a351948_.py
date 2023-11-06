"""empty message

Revision ID: 8a5c8a351948
Revises: 260d503a3c0d
Create Date: 2023-10-09 19:59:53.714021

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "8a5c8a351948"
down_revision = "260d503a3c0d"


def upgrade():
    op.create_table(
        "game_types",
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
    )
    op.create_table(
        "games",
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
        sa.Column("game_type_id", sa.Integer(), nullable=False),
        sa.Column("rounds", sa.Integer(), nullable=False),
        sa.Column("practice", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="sessions_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["game_type_id"], ["game_types.id"], name="games_game_type_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "game_players",
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
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name_hidden", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="game_players_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["game_id"], ["games.id"], name="game_players_game_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="game_players_player_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "game_answers",
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
        sa.Column("game_player_id", sa.Integer(), nullable=False),
        sa.Column("player_answer", sa.String(length=1), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["game_player_id"],
            ["game_players.id"],
            name="game_answers_game_players_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_constraint(
        "denirs_created_by_session_id_fkey", "denirs", type_="foreignkey"
    )
    op.drop_constraint(
        "player_survey_answers_player_id_fkey",
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
    op.execute("DROP TABLE sessions CASCADE;")
    op.execute("DROP TABLE session_answers CASCADE;")
    op.execute("DROP TABLE session_types CASCADE;")
    op.execute("DROP TABLE session_players CASCADE;")
    op.add_column(
        "denirs", sa.Column("created_by_game_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "denirs_created_by_game_id_fkey",
        "denirs",
        "games",
        ["created_by_game_id"],
        ["id"],
    )
    op.drop_column("denirs", "created_by_session_id")
    op.execute(
        """
            INSERT INTO game_types
            (network, bag)
            VALUES
            ('integrated', 'RRRRBB'),
            ('segregated', 'RRRRBB'),
            ('self-selected', 'RRRRBB'),
            ('integrated', 'BBBBRR'),
            ('segregated', 'BBBBRR'),
            ('self-selected', 'BBBBRR')
        """
    )


def downgrade():
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
        "denirs",
        sa.Column(
            "created_by_session_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(
        "denirs_created_by_game_id_fkey", "denirs", type_="foreignkey"
    )
    op.create_foreign_key(
        "denirs_created_by_session_id_fkey",
        "denirs",
        "sessions",
        ["created_by_session_id"],
        ["id"],
    )
    op.drop_column("denirs", "created_by_game_id")
    op.create_table(
        "session_players",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=True,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_by", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "session_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "name_hidden", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "position", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="session_players_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            name="session_players_session_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="session_players_player_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="session_players_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "session_types",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=True,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("network", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("bag", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.CheckConstraint(
            "network::text = ANY (ARRAY['integrated'::character varying, "
            "'segregated'::character varying, "
            "'self-selected'::character varying]::text[])",
            name="network_options",
        ),
        sa.PrimaryKeyConstraint("id", name="session_types_pkey"),
        sa.UniqueConstraint("network", name="session_types_network_key"),
    )
    op.create_table(
        "session_answers",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=True,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "player_answer",
            sa.VARCHAR(length=1),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "correct_answer",
            sa.VARCHAR(length=1),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("round", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "session_player_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_player_id"],
            ["session_players.id"],
            name="session_answers_session_players_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="session_answers_pkey"),
    )
    op.create_table(
        "sessions",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(
                always=False,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=True,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_by", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "session_type_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("rounds", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "practice", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="sessions_created_by_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["session_type_id"],
            ["users.id"],
            name="sessions_session_type_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="sessions_pkey"),
    )
    op.drop_table("game_answers")
    op.drop_table("game_players")
    op.drop_table("games")
    op.drop_table("game_types")
