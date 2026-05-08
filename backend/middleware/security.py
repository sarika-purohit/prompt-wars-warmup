"""Security headers middleware for TripFlow AI.

Adds standard HTTP security headers to every response to protect
against common web vulnerabilities (clickjacking, MIME sniffing,
XSS, etc.).  These headers follow OWASP recommendations.

References:
    - https://owasp.org/www-project-secure-headers/
    - https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
"""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that injects security headers into every HTTP response.

    Headers applied:
        - ``X-Content-Type-Options: nosniff`` — prevents MIME-type sniffing.
        - ``X-Frame-Options: DENY`` — blocks clickjacking via iframes.
        - ``X-XSS-Protection: 1; mode=block`` — legacy XSS filter.
        - ``Referrer-Policy: strict-origin-when-cross-origin`` — limits
          referrer information leakage.
        - ``Permissions-Policy`` — restricts browser feature access.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and add security headers to the response.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            Response: The HTTP response with security headers injected.
        """
        response = await call_next(request)

        # SECURITY: Prevent MIME-type sniffing attacks
        response.headers["X-Content-Type-Options"] = "nosniff"

        # SECURITY: Block clickjacking via iframes
        response.headers["X-Frame-Options"] = "DENY"

        # SECURITY: Legacy XSS protection for older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # SECURITY: Control referrer information leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # SECURITY: Restrict access to sensitive browser features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(self)"
        )

        return response
