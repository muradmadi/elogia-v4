"""Service for sending outbound webhook requests to Clay."""
import httpx
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import settings


class ClayWebhookService:
    """Service for sending outbound webhook requests to Clay."""
    
    def __init__(self):
        """Initialize the Clay webhook service."""
        self.webhook_url = settings.clay_webhook_url
        self.auth_token = settings.clay_webhook_auth_token
        # Strip any trailing whitespace from public_base_url to prevent invalid URLs
        self.public_base_url = settings.public_base_url.strip()
    
    async def trigger_enrichment(
        self,
        email: str,
        job_id: UUID,
    ) -> Dict[str, Any]:
        """
        Send a POST request to Clay's webhook URL to trigger enrichment.
        
        Args:
            email: Email address to enrich
            job_id: Unique identifier for the enrichment job
            
        Returns:
            Dict containing Clay's response
            
        Raises:
            HTTPException: If the request to Clay fails
        """
        # Build callback URL using PUBLIC_BASE_URL with job_id parameter
        callback_url = f"{self.public_base_url}/webhooks/clay?job_id={job_id}"
        
        # Prepare payload for Clay
        payload = {
            "email": email,
            "job_id": str(job_id),
            "callback_url": callback_url,
        }
        
        # Prepare headers with authentication
        headers = {
            "Content-Type": "application/json",
            "x-clay-webhook-auth": self.auth_token,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                )
                
                # Check if request was successful
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Clay webhook request failed with status {response.status_code}: {response.text}",
                    )
                
                return {
                    "status": "success",
                    "clay_response": response.json(),
                    "job_id": str(job_id),
                    "email": email,
                }
                
        except httpx.RequestError as e:
            # Network or timeout errors
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Clay webhook: {str(e)}",
            )
        except Exception as e:
            # Unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error calling Clay webhook: {str(e)}",
            )
    
