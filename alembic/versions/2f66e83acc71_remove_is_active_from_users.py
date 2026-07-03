"""remove is_active from users

Revision ID: 2f66e83acc71
Revises: 9a247d8b06ef
Create Date: 2026-06-30 19:22:11.611882

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f66e83acc71"
down_revision: Union[str, Sequence[str], None] = "9a247d8b06ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("users", "is_active")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
