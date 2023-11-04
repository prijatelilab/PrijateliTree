"""empty message

Revision ID: 30991d313ac8
Revises: 21c9591d0d5d
Create Date: 2023-11-04 05:23:42.386910

"""
import sqlalchemy as sa
from alembic import op


revision = "30991d313ac8"
down_revision = "21c9591d0d5d"


def upgrade():
    op.create_unique_constraint(None, "high_schools", ["name"])
    op.add_column(
        "users",
        sa.Column(
            "uuid",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=True,
        ),
    )
    op.create_unique_constraint(None, "users", ["uuid"])
    # ### end Alembic commands ###


def downgrade():
    op.drop_constraint(None, "users", type_="unique")
    op.drop_column("users", "uuid")
    op.drop_constraint(None, "high_schools", type_="unique")
