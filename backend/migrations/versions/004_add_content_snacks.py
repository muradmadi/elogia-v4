"""Add ContentSnack model for storing content snippets from n8n shredder

Revision ID: 4b9c8d1e2f3a
Revises: 3a7b8c9d1e2f
Create Date: 2026-03-20 06:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4b9c8d1e2f3a'
down_revision = '3a7b8c9d1e2f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade operations."""
    # Create content_snacks table
    op.create_table('content_snacks',
                    sa.Column('id', sa.Uuid(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
                    sa.Column('asset_id', sa.Uuid(), nullable=False),
                    sa.Column('content_type', sa.String(length=50), nullable=False),
                    sa.Column('content_text', sa.Text(), nullable=False),
                    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['asset_id'], ['marketing_assets.id'], name='fk_content_snacks_asset_id')
                    )
    
    # Create indexes
    op.create_index(op.f('ix_content_snacks_asset_id'), 'content_snacks', ['asset_id'], unique=False)
    op.create_index(op.f('ix_content_snacks_content_type'), 'content_snacks', ['content_type'], unique=False)
    op.create_index(op.f('ix_content_snacks_created_at'), 'content_snacks', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade operations."""
    # Drop indexes
    op.drop_index(op.f('ix_content_snacks_created_at'), table_name='content_snacks')
    op.drop_index(op.f('ix_content_snacks_content_type'), table_name='content_snacks')
    op.drop_index(op.f('ix_content_snacks_asset_id'), table_name='content_snacks')
    
    # Drop content_snacks table
    op.drop_table('content_snacks')
