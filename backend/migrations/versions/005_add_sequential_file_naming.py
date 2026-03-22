"""Add sequential file naming to marketing_assets

Revision ID: 4b5c6d7e8f9a
Revises: 4b9c8d1e2f3a
Create Date: 2026-03-20 07:34:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b5c6d7e8f9a'
down_revision = '4b9c8d1e2f3a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade operations."""
    # Add original_filename column
    op.add_column('marketing_assets', sa.Column('original_filename', sa.String(length=255), nullable=True))
    
    # Add sequence_number column with index
    op.add_column('marketing_assets', sa.Column('sequence_number', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_marketing_assets_sequence_number'), 'marketing_assets', ['sequence_number'], unique=False)


def downgrade() -> None:
    """Downgrade operations."""
    # Drop sequence_number index and column
    op.drop_index(op.f('ix_marketing_assets_sequence_number'), table_name='marketing_assets')
    op.drop_column('marketing_assets', 'sequence_number')
    
    # Drop original_filename column
    op.drop_column('marketing_assets', 'original_filename')
