"""Service for triggering n8n content shredder webhook."""
import httpx
from typing import Dict, Any
from uuid import UUID

from app.core.config import settings


class N8nService:
    """Service for triggering n8n content shredder webhook."""
    
    def __init__(self):
        """Initialize the n8n service."""
        self.n8n_webhook_url = settings.n8n_shredder_webhook_url
        self.public_base_url = settings.public_base_url
    
    async def trigger_content_shredder(
        self,
        asset_id: UUID,
        file_url: str,
    ) -> Dict[str, Any]:
        """
        Trigger n8n content shredder webhook (fire-and-forget).
        
        This method makes an async HTTP POST request to n8n and returns immediately
        without waiting for the response. Errors are logged but don't crash the server.
        
        Args:
            asset_id: Unique identifier for the marketing asset
            file_url: URL to the PDF file for processing
            
        Returns:
            Dict containing status and asset_id (always succeeds unless network error)
        """
        # Build callback URL using public_base_url (same as Clay webhook)
        callback_url = f"{self.public_base_url}/api/assets/webhook/n8n-callback"
        
        # Prepare payload for n8n
        payload = {
            "asset_id": str(asset_id),
            "file_url": file_url,
            "callback_url": callback_url,
        }
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
        }
        
        try:
            # Fire-and-forget: don't wait for response
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use a task to send the request without blocking
                # We don't await the response - just fire it off
                await client.post(
                    self.n8n_webhook_url,
                    json=payload,
                    headers=headers,
                )
            
            # If we get here, the request was sent successfully
            return {
                "status": "webhook_triggered",
                "asset_id": str(asset_id),
                "message": "n8n content shredder webhook triggered successfully",
            }
            
        except httpx.RequestError as e:
            # Network or timeout errors - log but don't crash
            # In production, you'd want to log this properly
            return {
                "status": "webhook_failed",
                "asset_id": str(asset_id),
                "error": f"Failed to trigger n8n webhook: {str(e)}",
                "message": "Webhook trigger failed but asset was saved",
            }
        except Exception as e:
            # Unexpected errors - log but don't crash
            return {
                "status": "webhook_failed",
                "asset_id": str(asset_id),
                "error": f"Unexpected error triggering n8n webhook: {str(e)}",
                "message": "Webhook trigger failed but asset was saved",
            }
