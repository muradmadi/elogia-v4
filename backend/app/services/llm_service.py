"""LLM service for interacting with Anthropic API."""
import json
import logging
from typing import Optional

from anthropic import AsyncAnthropic
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.prompts import MASTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Anthropic LLM API."""
    
    def __init__(self):
        """Initialize the LLM service with AsyncAnthropic client."""
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def generate_sequence(
        self,
        payload_context: dict,
        model: str = "claude-haiku-4-5",
    ) -> dict:
        """Generate an 8-touch email sequence using Claude.
        
        Args:
            payload_context: The consolidated JSON payload with all context data.
            model: The Claude model to use (default: claude-haiku-4-5).
        
        Returns:
            dict: The parsed JSON response containing the 8-touch sequence.
        
        Raises:
            HTTPException: If the LLM call fails or response cannot be parsed.
        """
        try:
            # Stringify the payload context for the LLM
            context_str = json.dumps(payload_context, indent=2)
            
            # Call Claude with the master system prompt and context
            response = await self.client.messages.create(
                model=model,
                max_tokens=4000,
                system=MASTER_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Here is the consolidated JSON context:\n\n{context_str}",
                    }
                ],
            )
            
            # Extract the response text
            response_text = response.content[0].text
            
            # Clean up the response text to remove any markdown formatting
            # Claude sometimes hallucinates markdown backticks despite instructions
            cleaned_text = self._clean_response_text(response_text)
            
            # Parse the JSON response
            try:
                parsed_response = json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse LLM response as JSON: {e}\n"
                    f"Raw response: {response_text}\n"
                    f"Cleaned text: {cleaned_text}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to parse LLM response as JSON",
                )
            
            # Validate the response structure
            if "touches" not in parsed_response:
                logger.error(
                    f"LLM response missing 'touches' key: {parsed_response}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="LLM response missing required 'touches' key",
                )
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LLM generation failed: {str(e)}",
            )
    
    def _clean_response_text(self, text: str) -> str:
        """Clean up LLM response text by removing markdown formatting and extracting JSON.
        
        Args:
            text: The raw response text from Claude.
        
        Returns:
            str: The extracted JSON string.
        """
        import re
        
        # Try to extract a JSON object or array structure
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            return json_match.group(0).strip()
            
        # Fallback to just stripping whitespace if no clear JSON block is found
        return text.strip()


# Global LLM service instance
llm_service = LLMService()
