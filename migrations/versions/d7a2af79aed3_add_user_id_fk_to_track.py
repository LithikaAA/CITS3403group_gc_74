"""Add user_id FK to Track

Revision ID: d7a2af79aed3
Revises: c61f660578ee
Create Date: 2025-05-08 22:09:00.946038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7a2af79aed3'
down_revision = 'c61f660578ee'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tracks') as batch_op:
        # 1add the user_id column
        batch_op.add_column(
            sa.Column('user_id', sa.Integer(), nullable=False)
        )
        # create a named FK constraint to users.id
        batch_op.create_foreign_key(
            'fk_tracks_user_id_users',  # name of the constraint
            'users',                    # referent table
            ['user_id'],                # local cols
            ['id']                      # remote cols
        )

def downgrade():
    with op.batch_alter_table('tracks') as batch_op:
        batch_op.drop_constraint('fk_tracks_user_id_users', type_='foreignkey')
        batch_op.drop_column('user_id')


    # ### end Alembic commands ###
