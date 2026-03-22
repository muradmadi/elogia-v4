"""Fix datetime timezone for all tables

Revision ID: 7e8f9a0b1c2d
Revises: 6d7e8f9a0b1c
Create Date: 2026-03-21 12:24:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e8f9a0b1c2d'
down_revision = '6d7e8f9a0b1c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade operations."""
    # Fix enrichment_jobs table
    op.execute("ALTER TABLE enrichment_jobs ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE enrichment_jobs ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE")
    
    # Fix campaign_sequences table
    op.execute("ALTER TABLE campaign_sequences ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE campaign_sequences ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE")
    
    # Fix marketing_assets table
    op.execute("ALTER TABLE marketing_assets ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE marketing_assets ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE")
    
    # Fix content_snacks table
    op.execute("ALTER TABLE content_snacks ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE")
    op.execute("ALTER TABLE content_snacks ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE")


def downgrade() -> None:
    """Downgrade operations."""
    # Revert enrichment_jobs table
    op.execute("ALTER TABLE enrichment_jobs ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE enrichment_jobs ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    
    # Revert campaign_sequences table
    op.execute("ALTER TABLE campaign_sequences ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE campaign_sequences ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    
    # Revert marketing_assets table
    op.execute("ALTER TABLE marketing_assets ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE marketing_assets ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    
    # Revert content_snacks table
    op.execute("ALTER TABLE content_snacks ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE")
    op.execute("ALTER TABLE content_snacks ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE")
