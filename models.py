from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

Provider = Literal["dall-e-3", "bfl-flux"]

class GenerationRequest(BaseModel):
    provider: Provider = Field(..., description="The image generation provider to use.")
    prompt: str = Field(..., description="The text prompt to generate an image from.")
    n: int = Field(default=1, gt=0, le=4, description="The number of images to generate.")
    user_id: Optional[str] = Field(default=None, description="Optional end-user identifier.")
    provider_params: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific parameters.")
    input_image: Optional[str] = Field(default=None, description="Base64 image for img2img (BFL Kontext).")

class ImageResponse(BaseModel):
    image_url: str
    revised_prompt: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GatewayResponse(BaseModel):
    status: str = "success"
    provider_used: Provider
    data: List[ImageResponse]


