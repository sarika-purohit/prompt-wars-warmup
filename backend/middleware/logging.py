import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("tripflow.timing")

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request execution time."""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add custom header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log it
        if request.url.path not in ["/health", "/", "/docs", "/openapi.json"]:
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
            
        return response
