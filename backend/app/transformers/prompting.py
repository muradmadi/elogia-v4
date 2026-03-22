"""Transformer for Claude sequence response data."""
from typing import Dict, Any, List
from app.schemas.sequence import ClaudeOutreachView, TouchView, AccountStrategyView


def transform_sequence_response(raw_response: Dict[str, Any]) -> ClaudeOutreachView:
    """Transform raw Claude API response into validated ClaudeOutreachView.
    
    Args:
        raw_response: Raw JSON response from Claude's sequence generation
        
    Returns:
        ClaudeOutreachView: Validated and structured outreach sequence data
        
    Raises:
        ValidationError: If the response doesn't match the expected schema
    """
    # Extract touches from response
    touches_data = raw_response.get("touches", [])
    
    # Transform each touch
    touches: List[TouchView] = []
    for touch_data in touches_data:
        touch = TouchView(
            objective=touch_data.get("objective", ""),
            touch_number=touch_data.get("touch_number", 0),
            example_snippet=touch_data.get("example_snippet", ""),
            ai_prompt_instruction=touch_data.get("ai_prompt_instruction", ""),
        )
        touches.append(touch)
    
    # Transform account strategy analysis
    strategy_data = raw_response.get("account_strategy_analysis", {})
    account_strategy = AccountStrategyView(
        personalization_angle=strategy_data.get("personalization_angle", ""),
        identified_core_pain_point=strategy_data.get("identified_core_pain_point", ""),
    )
    
    # Build and validate the full response
    return ClaudeOutreachView(
        touches=touches,
        account_strategy_analysis=account_strategy,
    )


def validate_claude_response(raw_response: Dict[str, Any]) -> ClaudeOutreachView:
    """Quick validation of Claude response using Pydantic's model_validate.
    
    This is a simpler alternative when you just want to validate the response
    without additional transformation logic.
    
    Args:
        raw_response: Raw JSON response from Claude's sequence generation
        
    Returns:
        ClaudeOutreachView: Validated outreach sequence data
    """
    return ClaudeOutreachView.model_validate(raw_response)
