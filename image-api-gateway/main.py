import time
import logging
from fastapi import FastAPI, Depends, HTTPException, Request, status
from .models import GenerationRequest, GatewayResponse
from .auth import get_api_key
from .providers.dalle_adapter import DalleAdapter
from .providers.bfl_flux_adapter import BflFluxAdapter

app = FastAPI(
    title="Universal Image Generation API Gateway",
    description="A multi-provider API to generate images from DALL-E and BFL FLUX.",
    version="1.0.0",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROVIDER_ADAPTERS = {
    "dall-e-3": DalleAdapter(),
    "bfl-flux": BflFluxAdapter(),
}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Request finished: status_code={response.status_code} process_time={process_time:.4f}s")
    return response

@app.post(
    "/v1/images/generations",
    response_model=GatewayResponse,
    summary="Generate Images from Multiple Providers",
    tags=["Image Generation"]
)
async def create_image_generation(
    request: GenerationRequest,
    api_key: str = Depends(get_api_key)
):
    logger.info(f"Received generation request for provider: {request.provider}")

    adapter = PROVIDER_ADAPTERS.get(request.provider)
    if not adapter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{request.provider}' is not supported."
        )

    try:
        image_responses = await adapter.generate(
            prompt=request.prompt,
            n=request.n,
            provider_params=request.provider_params,
            input_image_b64=request.input_image
        )

        return GatewayResponse(
            provider_used=request.provider,
            data=image_responses
        )
    except HTTPException as e:
        logger.error(f"HTTP Error during generation for {request.provider}: {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"An unexpected error occurred for provider {request.provider}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred with the {request.provider} provider: {str(e)}"
        )


