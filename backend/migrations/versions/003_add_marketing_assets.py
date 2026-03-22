"""Add MarketingAsset model for PDF storage and content recycling

Revision ID: 3a7b8c9d1e2f
Revises: 2d5f2d6b5ddb
Create Date: 2026-03-20 06:28:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a7b8c9d1e2f'
down_revision = '2d5f2d6b5ddb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade operations."""
    # Create marketing_assets table
    op.create_table('marketing_assets',
                    sa.Column('id', sa.Uuid(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
                    sa.Column('filename', sa.String(length=255), nullable=False),
                    sa.Column('storage_url', sa.String(length=500), nullable=False),
                    sa.Column('status', sa.String(length=50), server_default='uploaded', nullable=False),
                    sa.Column('webhook_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_marketing_assets_filename'), 'marketing_assets', ['filename'], unique=False)


def downgrade() -> None:
    """Downgrade operations."""
    # Drop marketing_assets table
    op.drop_index(op.f('ix_marketing_assets_filename'), table_name='marketing_assets')
    op.drop_table('marketing_assets')
