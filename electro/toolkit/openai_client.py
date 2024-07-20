from openai import AsyncOpenAI

from ..settings import settings

async_openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
