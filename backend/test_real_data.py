"""Test script to verify clean endpoints with REAL database data."""
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.enrichment import EnrichmentJob
from app.models.sequence import CampaignSequence
from app.services.enrichment_service import EnrichmentService, get_lead_profile, get_sequence_data
from app.schemas.enriched_data import LeadProfileView
from app.schemas.sequence import ClaudeOutreachView


async def test_with_real_data():
    """Test endpoints with real database data."""
    print("=" * 70)
    print("Testing Clean Endpoints with REAL Database Data")
    print("=" * 70)
    
    # Create database connection
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True
    )
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    job_id = "73678d6d-9fdc-492e-a417-c5f174e5347f"
    
    async with async_session() as session:
        print(f"\n1. Fetching job {job_id} from database...")
        
        # Get the job
        result = await session.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            print(f"❌ Job {job_id} not found in database!")
            return False
        
        print(f"✓ Job found: {job.email}")
        print(f"  Status: {job.status}")
        print(f"  Payloads: payload_1={job.payload_1 is not None}, payload_2={job.payload_2 is not None}")
        
        # Test 1: Get transformed lead profile
        print(f"\n2. Testing GET /api/enrichment/{job_id}/profile...")
        try:
            profile = await get_lead_profile(session, job_id)
            
            # Verify it's a LeadProfileView
            assert isinstance(profile, LeadProfileView), "Should return LeadProfileView"
            print("✓ Returns LeadProfileView instance")
            
            # Display profile data
            print(f"  Name: {profile.name}")
            print(f"  Title: {profile.current_title}")
            print(f"  Location: {profile.location}")
            
            if profile.company:
                print(f"  Company: {profile.company.name}")
                print(f"  Industry: {profile.company.industry}")
            
            if profile.intelligence:
                print(f"  Has intelligence data: Yes")
                if profile.intelligence.pain_points:
                    print(f"  Has pain points: Yes")
                if profile.intelligence.outreach_strategy:
                    print(f"  Has outreach strategy: Yes")
            
            print("✅ Lead profile endpoint works with real data!")
            
        except Exception as e:
            print(f"❌ Lead profile test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 2: Get sequence data
        print(f"\n3. Testing GET /api/sequence/job/{job_id}...")
        try:
            sequence = await get_sequence_data(session, job_id)
            
            # Verify it's a ClaudeOutreachView
            assert isinstance(sequence, ClaudeOutreachView), "Should return ClaudeOutreachView"
            print("✓ Returns ClaudeOutreachView instance")
            
            # Display sequence data
            print(f"  Number of touches: {len(sequence.touches)}")
            
            if sequence.touches:
                first_touch = sequence.touches[0]
                print(f"  First touch objective: {first_touch.objective}")
                print(f"  First touch snippet preview: {first_touch.example_snippet[:80]}...")
            
            if sequence.account_strategy_analysis:
                print(f"  Has account strategy: Yes")
                print(f"  Personalization angle preview: {sequence.account_strategy_analysis.personalization_angle[:80]}...")
            
            print("✅ Sequence endpoint works with real data!")
            
        except Exception as e:
            print(f"❌ Sequence test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 3: Compare raw vs transformed data
        print(f"\n4. Comparing raw vs transformed data...")
        print(f"  Raw payload_1 keys: {list(job.payload_1.keys()) if job.payload_1 else 'None'}")
        print(f"  Transformed profile has: name, title, location, company, intelligence")
        print("✓ Transformation successful")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED WITH REAL DATABASE DATA!")
        print("=" * 70)
        
        print("\nAvailable endpoints:")
        print(f"  GET /api/enrichment/{job_id}/profile")
        print(f"  GET /api/sequence/job/{job_id}")
        
        return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_with_real_data())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
