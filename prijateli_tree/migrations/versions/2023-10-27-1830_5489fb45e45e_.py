"""empty message

Revision ID: 5489fb45e45e
Revises: 8a5c8a351948
Create Date: 2023-10-27 18:30:15.078524

"""
import sqlalchemy as sa
from alembic import op


revision = "5489fb45e45e"
down_revision = "8a5c8a351948"


def upgrade():
    op.create_table(
        "high_schools",
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "users", sa.Column("qualtrics_id", sa.String(), nullable=True)
    )
    op.add_column(
        "users", sa.Column("grade_level", sa.Integer(), nullable=True)
    )
    op.add_column(
        "users", sa.Column("high_school_id", sa.Integer(), nullable=True)
    )
    op.drop_constraint("users_phone_number_key", "users", type_="unique")
    op.create_foreign_key(
        "users_high_schools_id_fkey",
        "users",
        "high_schools",
        ["high_school_id"],
        ["id"],
    )
    op.drop_column("users", "phone_number")
    op.execute(
        """
        INSERT INTO high_schools
            (name)
        VALUES
            ('Medical High School'),
            ('Gymnasium High School'),
            ('Technical High School');
        """
    )


def downgrade():
    op.add_column(
        "users",
        sa.Column(
            "phone_number", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        "users_high_schools_id_fkey", "users", type_="foreignkey"
    )
    op.create_unique_constraint(
        "users_phone_number_key", "users", ["phone_number"]
    )
    op.drop_column("users", "high_school_id")
    op.drop_column("users", "grade_level")
    op.drop_column("users", "qualtrics_id")
    op.drop_table("high_schools")
