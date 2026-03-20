"""Test script to verify the clean data endpoints work correctly."""
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.enrichment_service import EnrichmentService
from app.schemas.enriched_data import LeadProfileView
from app.schemas.sequence import ClaudeOutreachView
from app.transformers import validate_claude_outreach

# Mock job data for testing
class MockJob:
    def __init__(self):
        self.job_id = "73678d6d-9fdc-492e-a417-c5f174e5347f"
        self.email = "test@example.com"
        self.status = "completed"
        self.payload_1 = {
            "name": "Test Person",
            "title": "VP Test",
            "location_name": "Paris, France",
            "url": "https://linkedin.com/in/test",
            "headline": "Test Headline",
            "summary": "Test Summary",
            "experience": [],
            "education": [],
            "languages": []
        }
        self.payload_2 = {
            "name": "Test Company",
            "domain": "test.com",
            "industry": "Technology",
            "size": "1000-5000 employees",
            "revenue": "100M-500M",
            "headquarters": "Paris, France",
            "description": "Test company description",
            "specialties": [],
            "business_tags": []
        }
        self.payload_3 = {}
        self.payload_4 = {}
        self.payload_5 = {}
        self.payload_6 = {}


class MockSequence:
    def __init__(self):
        self.sequence_data = {
            "touches": [
                {
                    "objective": "Test objective",
                    "touch_number": 1,
                    "example_snippet": "Test snippet",
                    "ai_prompt_instruction": "Test instruction"
                }
            ],
            "account_strategy_analysis": {
                "personalization_angle": "Test angle",
                "identified_core_pain_point": "Test pain point"
            }
        }


async def test_lead_profile_endpoint():
    """Test the lead profile endpoint."""
    print("Testing lead profile endpoint...")
    
    try:
        # Test with mock job
        mock_job = MockJob()
        profile = await EnrichmentService.build_profile_from_job(mock_job)
        
        # Verify it's a LeadProfileView
        assert isinstance(profile, LeadProfileView), "Should return LeadProfileView"
        print("✓ Returns LeadProfileView instance")
        
        # Verify person data
        assert profile.name == "Test Person"
        assert profile.current_title == "VP Test"
        print("✓ Person data is correctly populated")
        
        # Verify company data
        assert profile.company is not None
        assert profile.company.name == "Test Company"
        print("✓ Company data is correctly populated")
        
        print("✅ Lead profile endpoint test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Lead profile test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_sequence_endpoint():
    """Test the sequence endpoint."""
    print("\nTesting sequence endpoint...")
    
    try:
        # Test with mock sequence
        mock_sequence = MockSequence()
        sequence = validate_claude_outreach(mock_sequence.sequence_data)
        
        # Verify it's a ClaudeOutreachView
        assert isinstance(sequence, ClaudeOutreachView), "Should return ClaudeOutreachView"
        print("✓ Returns ClaudeOutreachView instance")
        
        # Verify touches
        assert len(sequence.touches) == 1
        assert sequence.touches[0].objective == "Test objective"
        print("✓ Touches are correctly populated")
        
        # Verify account strategy
        assert sequence.account_strategy_analysis is not None
        assert sequence.account_strategy_analysis.personalization_angle == "Test angle"
        print("✓ Account strategy is correctly populated")
        
        print("✅ Sequence endpoint test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Sequence endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    # Note: These tests use mock data since we can't test with actual database
    # The actual endpoints will work with real data
    
    print("=" * 60)
    print("Testing Clean Data Endpoints")
    print("=" * 60)
    
    success1 = await test_lead_profile_endpoint()
    success2 = await test_sequence_endpoint()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All endpoint tests passed!")
        print("\nEndpoints available:")
        print("  GET /api/enrichment/{job_id}/profile")
        print("  GET /api/sequence/job/{job_id}")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All endpoint tests passed!")
        print("\nEndpoints available:")
        print("  GET /api/enrichment/{job_id}/profile")
        print("  GET /api/sequence/job/{job_id}")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
