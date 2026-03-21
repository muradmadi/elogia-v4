"""Pydantic schemas for email sequence generation data."""
from pydantic import Field
from typing import List, Optional

from .base import BaseSchema

class TouchView(BaseSchema):
    objective: str = Field(description="Goal of this outreach touch (e.g., Observation/Relevance hook, Value delivery)")
    touch_number: int = Field(description="Sequential number of the touch (1‑based)")
    example_snippet: str = Field(description="Concrete example email snippet in Spanish")
    ai_prompt_instruction: str = Field(description="Instructions that were given to the AI to generate the snippet")

class AccountStrategyView(BaseSchema):
    personalization_angle: str = Field(description="High-level strategic angle for approaching the lead, including the core thesis and how to position Elogia")
    identified_core_pain_point: str = Field(description="The central pain point of the lead that the outreach strategy addresses")

class ClaudeOutreachView(BaseSchema):
    touches: List[TouchView] = Field(description="Array of outreach touches, each with an example snippet and AI prompt")
    account_strategy_analysis: AccountStrategyView = Field(description="Overarching strategic analysis that informs the outreach sequence")