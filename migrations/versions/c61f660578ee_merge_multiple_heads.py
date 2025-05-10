"""Merge multiple heads

Revision ID: c61f660578ee
Revises: 42ffe72905de, ba1e24a217b8
Create Date: 2025-05-08 22:01:13.685119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c61f660578ee'
down_revision = ('42ffe72905de', 'ba1e24a217b8')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
