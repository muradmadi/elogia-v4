"""Rename metadata to content_metadata in content_snacks

Revision ID: 6d7e8f9a0b1c
Revises: 5c6d7e8f9a0b
Create Date: 2026-03-21 12:04:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d7e8f9a0b1c'
down_revision = '5c6d7e8f9a0b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade operations."""
    # Rename the metadata column to content_metadata in content_snacks table
    op.alter_column(
        'content_snacks',
        'metadata',
        new_column_name='content_metadata',
        existing_type=sa.dialects.postgresql.JSONB,
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade operations."""
    # Revert the column name back to metadata
    op.alter_column(
        'content_snacks',
        'content_metadata',
        new_column_name='metadata',
        existing_type=sa.dialects.postgresql.JSONB,
        existing_nullable=True,
    )
