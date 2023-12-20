"""empty message

Revision ID: e07d61e85a9d
Revises: 2a3cc1015699
Create Date: 2023-12-20 23:33:32.844322

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "e07d61e85a9d"
down_revision = "2a3cc1015699"


def upgrade():
    op.create_table(
        "denars",
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
            name="creation_check",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_session_id"],
            ["game_sessions.id"],
            name="denars_created_by_session_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="denars_created_by_user_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.drop_table("denirs")


def downgrade():
    op.create_table(
        "denirs",
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
            "created_by_user_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "external_id", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("amount", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "created_by_session_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["created_by_session_id"],
            ["game_sessions.id"],
            name="denirs_created_by_session_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="denirs_created_by_user_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="denirs_pkey"),
        sa.UniqueConstraint("external_id", name="denirs_external_id_key"),
    )
    op.drop_table("denars")
