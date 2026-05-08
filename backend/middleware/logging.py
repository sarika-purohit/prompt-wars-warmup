"""Request timing middleware for performance monitoring.

Logs the HTTP method, path, status code, and wall-clock duration
of every non-trivial API request.  This data feeds into Cloud Logging
for production observability and helps identify slow endpoints.

Efficiency:
    Uses ``time.perf_counter()`` for high-resolution timing.
    Adds an ``X-Process-Time`` header so clients can observe latency.
"""

from __future__ import annotations

import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("tripflow.timing")

# Paths excluded from timing logs to reduce noise
_EXCLUDED_PATHS = frozenset({"/health", "/", "/docs", "/openapi.json"})


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware that measures and logs request processing time.

    Attaches an ``X-Process-Time`` response header (in seconds) and
    logs timing data for non-health-check endpoints.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Measure request duration and log it.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The HTTP response with ``X-Process-Time`` header.
        """
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # EFFICIENCY: Add timing header for client-side performance monitoring
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # Only log non-trivial API requests to reduce log volume
        if request.url.path not in _EXCLUDED_PATHS:
            logger.info(
                "%s %s — Status: %d — Time: %.4fs",
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )

        return response
