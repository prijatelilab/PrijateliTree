"""empty message

Revision ID: e5b498dd07a6
Revises: 47fe187bc716
Create Date: 2023-10-06 16:24:21.643648

"""
from alembic import op
import sqlalchemy as sa



revision = 'e5b498dd07a6'
down_revision = '47fe187bc716'


def upgrade():
    op.execute(
        """
            INSERT INTO session_types
            (name, abbr)
            VALUES
            ('English', 'EN'),
            ('Macedonian', 'MK'),
            ('Albanian', 'SQ'),
            ('Turkish', 'TR')
        """
    )


def downgrade():
    op.execute(
        """
            DELETE FROM languages;
        """
    )