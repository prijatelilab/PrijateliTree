"""empty message

Revision ID: 169b451d6f2d
Revises: 2904026841be
Create Date: 2023-11-27 23:19:06.427974

"""
from alembic import op
import sqlalchemy as sa



revision = '169b451d6f2d'
down_revision = '2904026841be'


def upgrade():
    op.execute(
        """
        INSERT INTO high_schools
            (name)
        VALUES
            ('Goce Delcev Middle School')
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM high_schools
        WHERE name = 'Goce Delcev Middle School'
        """
    )
