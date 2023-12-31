"""empty message

Revision ID: e5b498dd07a6
Revises: 47fe187bc716
Create Date: 2023-10-06 16:24:21.643648

"""
from alembic import op


revision = "e5b498dd07a6"
down_revision = "47fe187bc716"


def upgrade():
    op.execute(
        """
            INSERT INTO languages
            (name, abbr)
            VALUES
            ('English', 'en'),
            ('Macedonian', 'mk'),
            ('Albanian', 'sq'),
            ('Turkish', 'tr')
        """
    )


def downgrade():
    op.execute(
        """
            DELETE FROM languages;
        """
    )
