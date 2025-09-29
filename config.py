import os
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GATEWAY_API_KEYS: List[str]
    OPENAI_API_KEY: str
    BFL_API_KEY: str

    class Config:
        env_file = ".env"
        fields = {
            'GATEWAY_API_KEYS': {
                'env_separator': ','
            }
        }

settings = Settings()


