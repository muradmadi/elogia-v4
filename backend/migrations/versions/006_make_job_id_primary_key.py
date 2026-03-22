"""Make job_id the primary key on EnrichmentJob

Revision ID: 5c6d7e8f9a0b
Revises: 4b5c6d7e8f9a
Create Date: 2026-03-20 21:19:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c6d7e8f9a0b'
down_revision = '4b5c6d7e8f9a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade operations."""
    # Get database inspector to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if foreign key constraint exists before dropping
    campaign_fks = inspector.get_foreign_keys('campaign_sequences')
    fk_exists = any(fk['name'] == 'campaign_sequences_enrichment_job_id_fkey' for fk in campaign_fks)
    
    if fk_exists:
        # Drop the foreign key constraint in campaign_sequences first
        op.drop_constraint(
            'campaign_sequences_enrichment_job_id_fkey',
            'campaign_sequences',
            type_='foreignkey'
        )
    
    # Check if id column exists before dropping
    enrichment_columns = [col['name'] for col in inspector.get_columns('enrichment_jobs')]
    
    if 'id' in enrichment_columns:
        # Drop the id column from enrichment_jobs
        op.drop_column('enrichment_jobs', 'id')
    
    # Check if primary key constraint exists and get its name
    pk_constraint = inspector.get_pk_constraint('enrichment_jobs')
    
    if pk_constraint and pk_constraint.get('name'):
        # Drop the existing primary key constraint
        op.drop_constraint(pk_constraint['name'], 'enrichment_jobs', type_='primary')
    
    # Make job_id the primary key (only if not already primary key)
    if pk_constraint.get('constrained_columns') != ['job_id']:
        op.create_primary_key(
            'enrichment_jobs_pkey',
            'enrichment_jobs',
            ['job_id']
        )
    
    # Check if foreign key already exists before creating
    enrichment_fks = inspector.get_foreign_keys('enrichment_jobs')
    fk_to_create = any(
        fk['name'] == 'campaign_sequences_enrichment_job_id_fkey'
        for fk in inspector.get_foreign_keys('campaign_sequences')
    )
    
    if not fk_to_create:
        # Update the foreign key in campaign_sequences to reference job_id
        op.create_foreign_key(
            'campaign_sequences_enrichment_job_id_fkey',
            'campaign_sequences',
            'enrichment_jobs',
            ['enrichment_job_id'],
            ['job_id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    """Downgrade operations."""
    # Get database inspector to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if foreign key constraint exists before dropping
    campaign_fks = inspector.get_foreign_keys('campaign_sequences')
    fk_exists = any(fk['name'] == 'campaign_sequences_enrichment_job_id_fkey' for fk in campaign_fks)
    
    if fk_exists:
        # Drop the foreign key constraint in campaign_sequences
        op.drop_constraint(
            'campaign_sequences_enrichment_job_id_fkey',
            'campaign_sequences',
            type_='foreignkey'
        )
    
    # Check if primary key constraint exists and get its name
    pk_constraint = inspector.get_pk_constraint('enrichment_jobs')
    
    if pk_constraint and pk_constraint.get('name'):
        # Drop the primary key constraint on job_id
        op.drop_constraint(pk_constraint['name'], 'enrichment_jobs', type_='primary')
    
    # Check if id column already exists
    enrichment_columns = [col['name'] for col in inspector.get_columns('enrichment_jobs')]
    
    if 'id' not in enrichment_columns:
        # Add back the id column as primary key
        op.add_column(
            'enrichment_jobs',
            sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False)
        )
    
    # Create primary key on id if not already exists
    if pk_constraint.get('constrained_columns') != ['id']:
        op.create_primary_key(
            'enrichment_jobs_pkey',
            'enrichment_jobs',
            ['id']
        )
    
    # Check if job_id column exists and is not the primary key
    if 'job_id' not in enrichment_columns:
        # Add back the job_id column as a separate column
        op.add_column(
            'enrichment_jobs',
            sa.Column('job_id', sa.UUID(), nullable=False)
        )
    
    # Check if index exists before creating
    enrichment_indexes = inspector.get_indexes('enrichment_jobs')
    index_exists = any(idx['name'] == 'ix_enrichment_jobs_job_id' for idx in enrichment_indexes)
    
    if not index_exists:
        op.create_index(
            'ix_enrichment_jobs_job_id',
            'enrichment_jobs',
            ['job_id'],
            unique=False
        )
    
    # Check if foreign key already exists before creating
    campaign_fks_after = inspector.get_foreign_keys('campaign_sequences')
    fk_to_create = any(
        fk['name'] == 'campaign_sequences_enrichment_job_id_fkey'
        for fk in campaign_fks_after
    )
    
    if not fk_to_create:
        # Update the foreign key in campaign_sequences to reference the id column
        op.create_foreign_key(
            'campaign_sequences_enrichment_job_id_fkey',
            'campaign_sequences',
            'enrichment_jobs',
            ['enrichment_job_id'],
            ['id'],
            ondelete='CASCADE'
        )
