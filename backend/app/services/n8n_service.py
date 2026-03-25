"""Service for triggering n8n content shredder webhook."""
import httpx
from typing import Dict, Any
from uuid import UUID

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


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
                response = await client.post(
                    self.n8n_webhook_url,
                    json=payload,
                    headers=headers,
                )
                
                # Check for HTTP errors like 404 Not Found
                response.raise_for_status()
            
            logger.info(f"Triggered n8n shredder successfully for asset {asset_id}")
            
            # If we get here, the request was sent successfully
            return {
                "status": "webhook_triggered",
                "asset_id": str(asset_id),
                "message": "n8n content shredder webhook triggered successfully",
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"n8n webhook returned error status {e.response.status_code} for asset {asset_id}: {e.response.text}")
            return {
                "status": "webhook_failed",
                "asset_id": str(asset_id),
                "error": f"Webhook returned HTTP {e.response.status_code}",
                "message": "Webhook trigger failed but asset was saved",
            }
        except httpx.RequestError as e:
            # Network or timeout errors
            logger.error(f"Network error triggering n8n webhook for asset {asset_id}: {str(e)}")
            return {
                "status": "webhook_failed",
                "asset_id": str(asset_id),
                "error": f"Failed to trigger n8n webhook: {str(e)}",
                "message": "Webhook trigger failed but asset was saved",
            }
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error triggering n8n webhook for asset {asset_id}: {str(e)}", exc_info=True)
            return {
                "status": "webhook_failed",
                "asset_id": str(asset_id),
                "error": f"Unexpected error triggering n8n webhook: {str(e)}",
                "message": "Webhook trigger failed but asset was saved",
            }
