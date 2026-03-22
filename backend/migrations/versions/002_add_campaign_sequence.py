"""Add CampaignSequence model with relationships to EnrichmentJob

Revision ID: 2d5f2d6b5ddb
Revises: 001
Create Date: 2026-03-19 23:26:11.536290

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2d5f2d6b5ddb'
down_revision = '001'
branch_labels = None
depends_on = None

# Constants for maintainability
PAYLOAD_COLUMNS = ['payload_1', 'payload_2', 'payload_3',
                   'payload_4', 'payload_5', 'payload_6']


def upgrade() -> None:
    """Upgrade operations."""
    # 1. Make enrichment_jobs.job_id unique
    op.drop_index('ix_enrichment_jobs_job_id', table_name='enrichment_jobs')
    op.create_index(op.f('ix_enrichment_jobs_job_id'), 'enrichment_jobs', ['job_id'], unique=True)

    # 2. Convert all JSON payload columns to JSONB
    for column in PAYLOAD_COLUMNS:
        op.alter_column('enrichment_jobs', column,
                        existing_type=postgresql.JSON(astext_type=sa.Text()),
                        type_=postgresql.JSONB(astext_type=sa.Text()),
                        existing_nullable=True)

    # 3. Create campaign_sequences table
    op.create_table('campaign_sequences',
                    sa.Column('id', sa.Uuid(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
                    sa.Column('enrichment_job_id', sa.UUID(), nullable=False),
                    sa.Column('master_prompt_used', sa.String(), nullable=True),
                    sa.Column('sequence_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.Column('status', sa.String(length=50), server_default='pending', nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['enrichment_job_id'], ['enrichment_jobs.job_id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_campaign_sequences_enrichment_job_id'), 'campaign_sequences', ['enrichment_job_id'], unique=True)


def downgrade() -> None:
    """Downgrade operations."""
    # 1. Drop campaign_sequences table
    op.drop_index(op.f('ix_campaign_sequences_enrichment_job_id'), table_name='campaign_sequences')
    op.drop_table('campaign_sequences')

    # 2. Revert JSONB columns back to JSON
    for column in reversed(PAYLOAD_COLUMNS):
        op.alter_column('enrichment_jobs', column,
                        existing_type=postgresql.JSONB(astext_type=sa.Text()),
                        type_=postgresql.JSON(astext_type=sa.Text()),
                        existing_nullable=True)

    # 3. Revert job_id index back to non-unique
    op.drop_index(op.f('ix_enrichment_jobs_job_id'), table_name='enrichment_jobs')
    op.create_index('ix_enrichment_jobs_job_id', 'enrichment_jobs', ['job_id'], unique=False)
