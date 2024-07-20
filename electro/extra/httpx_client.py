"""
The main (global) `httpx` client.

Used to (apparently) be able to async/await multiple web requests at the same time.

Whether this client preserves cookies or not remains a mystery to me. However, I'm not sure if it's relevant
to the bot's use case.

If you're reading this, you might as well check the `httpx` documentation to find out and let me know.
"""

import httpx

from ..settings import settings

httpx_client = httpx.AsyncClient(timeout=settings.HTTPX_CLIENT_DEFAULT_TIMEOUT)
