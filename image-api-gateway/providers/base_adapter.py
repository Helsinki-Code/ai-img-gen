from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..models import ImageResponse

class BaseAdapter(ABC):
    """
    Abstract Base Class (ABC) for all provider adapters.
    This defines a contract that all adapters must follow, ensuring they
    can be used interchangeably by the main application logic.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        n: int,
        provider_params: Dict[str, Any],
        input_image_b64: Optional[str] = None
    ) -> List[ImageResponse]:
        """
        The core method for generating images.

        Args:
            prompt (str): The text prompt.
            n (int): The number of images to generate.
            provider_params (Dict[str, Any]): Provider-specific parameters.
            input_image_b64 (Optional[str]): Base64 encoded input image for img2img tasks.

        Returns:
            List[ImageResponse]: A list of standardized image response objects.
        """
        pass


