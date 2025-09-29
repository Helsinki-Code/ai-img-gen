import httpx
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from .base_adapter import BaseAdapter
from ..models import ImageResponse
from ..config import settings

class DalleAdapter(BaseAdapter):
    """
    Adapter for interacting with the OpenAI DALL-E 3 API.
    """
    API_URL = "https://api.openai.com/v1/images/generations"

    async def generate(
        self,
        prompt: str,
        n: int,
        provider_params: Dict[str, Any],
        input_image_b64: Optional[str] = None
    ) -> List[ImageResponse]:
        
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        dalle_payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": n,
            "size": provider_params.get("size", "1024x1024"),
            "quality": provider_params.get("quality", "standard"),
            "style": provider_params.get("style", "vivid"),
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(self.API_URL, json=dalle_payload, headers=headers)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                error_detail = "No details provided."
                try:
                    error_detail = e.response.json().get("error", {}).get("message", error_detail)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Error from DALL-E API: {error_detail}"
                )

        data = response.json()["data"]
        return [
            ImageResponse(
                image_url=item["url"],
                revised_prompt=item.get("revised_prompt"),
                metadata={"model": "dall-e-3"}
            ) for item in data
        ]


