"""empty message

Revision ID: 8d6d2f92cb84
Revises: 0735fdd31631
Create Date: 2023-11-20 20:30:45.989585

"""
import sqlalchemy as sa
from alembic import op


revision = "8d6d2f92cb84"
down_revision = "0735fdd31631"


def upgrade():
    op.drop_column("game_players", "name_hidden")
    op.add_column(
        "game_types",
        sa.Column(
            "names_hidden", sa.Boolean(), server_default="false", nullable=False
        ),
    )
    op.execute(
        """
            INSERT INTO game_types
            (network, bag, names_hidden)
            VALUES
            ('integrated', 'RRRRBB', TRUE),
            ('segregated', 'RRRRBB', TRUE),
            ('self-selected', 'RRRRBB', TRUE),
            ('integrated', 'BBBBRR', TRUE),
            ('segregated', 'BBBBRR', TRUE),
            ('self-selected', 'BBBBRR', TRUE);
        """
    )


def downgrade():
    op.drop_column("game_types", "names_hidden")
    op.add_column(
        "game_players",
        sa.Column(
            "name_hidden", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
    )
    op.execute(
        """
            DELETE FROM game_types
            WHERE names_hidden = TRUE;
        """
    )
