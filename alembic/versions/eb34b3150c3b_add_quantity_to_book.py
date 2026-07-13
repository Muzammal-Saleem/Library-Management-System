"""add_quantity_to_book

Revision ID: eb34b3150c3b
Revises: 286a35627aba
Create Date: 2026-07-13 04:48:48.967841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb34b3150c3b'
down_revision: Union[str, Sequence[str], None] = '286a35627aba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('books', sa.Column('quantity', sa.Integer(), nullable=True))
    op.execute("UPDATE books SET quantity = 1")
    op.alter_column('books', 'quantity', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('books', 'quantity')
