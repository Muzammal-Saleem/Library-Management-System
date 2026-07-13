"""add_member_auth_and_roles

Revision ID: ff8d7f219ad8
Revises: f1eebb692574
Create Date: 2026-07-08 05:16:08.479868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff8d7f219ad8'
down_revision: Union[str, Sequence[str], None] = 'f1eebb692574'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the custom PostgreSQL enum type first
    member_role_enum = sa.Enum('Librarian', 'Member', name='member_role_enum')
    member_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('members', sa.Column('hashed_password', sa.String(length=255), nullable=False))
    op.add_column('members', sa.Column('role', member_role_enum, nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('members', 'role')
    op.drop_column('members', 'hashed_password')

    # Drop the custom PostgreSQL enum type
    sa.Enum(name='member_role_enum').drop(op.get_bind(), checkfirst=True)
