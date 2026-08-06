"""add unique constraint to images filename

Revision ID: bc15d5de8a42
Revises: 238d0d0252b7
Create Date: 2026-08-06 10:58:41.298923

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "bc15d5de8a42"
down_revision: Union[str, Sequence[str], None] = "238d0d0252b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uq_images_filename", "images", ["filename"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_images_filename", "images", type_="unique")
