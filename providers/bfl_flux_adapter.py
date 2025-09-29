import httpx
import asyncio
import time
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from .base_adapter import BaseAdapter
from ..models import ImageResponse
from ..config import settings

class BflFluxAdapter(BaseAdapter):
    """
    Adapter for interacting with the Black Forest Labs (BFL) FLUX API.
    This adapter handles the asynchronous, polling-based nature of the BFL API.
    """
    BASE_URL = "https://api.bfl.ai/v1"
    POLLING_INTERVAL_SECONDS = 2
    POLLING_TIMEOUT_SECONDS = 300

    async def generate(
        self,
        prompt: str,
        n: int,
        provider_params: Dict[str, Any],
        input_image_b64: Optional[str] = None
    ) -> List[ImageResponse]:

        model = provider_params.get("model")
        if not model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 'model' parameter is required in provider_params for BFL FLUX (e.g., 'flux-kontext-pro')."
            )

        headers = {
            "x-key": settings.BFL_API_KEY,
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        
        tasks = [
            self._generate_single_image(prompt, provider_params, headers, input_image_b64)
            for _ in range(n)
        ]
        
        results = await asyncio.gather(*tasks)
        return results

    async def _generate_single_image(
        self,
        prompt: str,
        provider_params: Dict[str, Any],
        headers: Dict[str, str],
        input_image_b64: Optional[str]
    ) -> ImageResponse:
        
        model_endpoint = provider_params.get("model")
        submit_url = f"{self.BASE_URL}/{model_endpoint}"

        payload = {
            "prompt": prompt,
            **{k: v for k, v in provider_params.items() if k != "model"}
        }

        if input_image_b64:
            payload["input_image"] = input_image_b64

        async with httpx.AsyncClient(timeout=self.POLLING_TIMEOUT_SECONDS) as client:
            try:
                submit_response = await client.post(submit_url, json=payload, headers=headers)
                submit_response.raise_for_status()
                submit_data = submit_response.json()
                
                polling_url = submit_data.get("polling_url")
                if not polling_url:
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "BFL API did not return a polling_url.")

                start_time = time.time()
                while time.time() - start_time < self.POLLING_TIMEOUT_SECONDS:
                    await asyncio.sleep(self.POLLING_INTERVAL_SECONDS)
                    
                    poll_response = await client.get(polling_url, headers=headers)
                    poll_response.raise_for_status()
                    poll_data = poll_response.json()

                    status_val = poll_data.get("status")
                    if status_val == "Ready":
                        result_url = poll_data.get("result", {}).get("sample")
                        if not result_url:
                             raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Generation succeeded but no result URL was found.")
                        
                        return ImageResponse(
                            image_url=result_url,
                            metadata={"model": model_endpoint, "request_id": poll_data.get("id")}
                        )
                    elif status_val in ["Error", "Failed", "Task not found"]:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"BFL image generation failed with status: {status_val}. Details: {poll_data.get('details', 'N/A')}"
                        )
                
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="BFL image generation timed out after polling."
                )

            except httpx.HTTPStatusError as e:
                error_detail = "No details provided."
                try:
                    error_detail = e.response.json()
                except Exception:
                    pass
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Error from BFL API: {error_detail}"
                )


