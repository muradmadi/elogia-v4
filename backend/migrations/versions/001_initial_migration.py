"""Initial migration for EnrichmentJob table.

Revision ID: 001
Revises: 
Create Date: 2026-03-19 12:00:00.000000+00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the enrichment_jobs table."""
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.create_table(
        "enrichment_jobs",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="pending", nullable=False),
        sa.Column("payload_1", sa.JSON(), nullable=True),
        sa.Column("payload_2", sa.JSON(), nullable=True),
        sa.Column("payload_3", sa.JSON(), nullable=True),
        sa.Column("payload_4", sa.JSON(), nullable=True),
        sa.Column("payload_5", sa.JSON(), nullable=True),
        sa.Column("payload_6", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes
    op.create_index(
        "ix_enrichment_jobs_job_id",
        "enrichment_jobs",
        ["job_id"],
        unique=False,
    )
    op.create_index(
        "ix_enrichment_jobs_email",
        "enrichment_jobs",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the enrichment_jobs table."""
    op.drop_index("ix_enrichment_jobs_email", table_name="enrichment_jobs")
    op.drop_index("ix_enrichment_jobs_job_id", table_name="enrichment_jobs")
    op.drop_table("enrichment_jobs")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
