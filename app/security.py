import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .models import UserRole
from .config import settings

def validate_ruet_email(email: str, role: UserRole) -> None:
    """
    Enforces RUET institutional email policy:
    - STUDENT: Must contain both 'student' and 'ruet' (e.g., 2203098@student.ruet.ac.bd)
    - FACULTY: Must contain 'ruet' (e.g., teacher@dept.ruet.ac.bd)
    - STAFF:   Must contain 'ruet' (e.g., staff@ruet.ac.bd)
    - ADMIN:   Must be in authorized admin list
    """
    e = (email or "").lower().strip()
    
    if role == UserRole.STUDENT:
        if "student" not in e or "ruet" not in e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Students must enter their official RUET student email containing both 'student' and 'ruet' (e.g., 2203098@student.ruet.ac.bd)."
            )
    elif role == UserRole.FACULTY:
        if "ruet" not in e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teachers/Faculty must enter their official RUET email containing 'ruet' (e.g., teacher@dept.ruet.ac.bd)."
            )
    elif role == UserRole.STAFF:
        if "ruet" not in e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Staff must enter their official RUET email containing 'ruet' (e.g., staff@ruet.ac.bd)."
            )
    elif role == UserRole.ADMIN:
        admin_emails = [a.lower().strip() for a in [settings.admin_one, settings.admin_two] if a]
        if e not in admin_emails:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This email is not authorized for the Admin role."
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects standard OWASP security headers to protect against clickjacking,
    MIME sniffing, cross-site scripting (XSS), and enforce HTTPS.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent Clickjacking (allow embedding only by same origin for UI modals)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # Enable legacy browser XSS filters
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Disallow unwanted browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Enforce HTTPS HSTS when in production
        if settings.environment.lower() == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    In-memory Sliding Window Rate Limiter.
    Protects against brute force and DDoS on authentication, AI chatbot, and sensitive endpoints.
    No heavy Redis dependency required.
    """
    # path_prefix: (max_requests, window_seconds)
    ROUTE_LIMITS: List[Tuple[str, int, int]] = [
        ("/auth/login", 10, 60),      # 10 login attempts per min
        ("/auth/register", 5, 60),    # 5 registrations per min
        ("/auth/forget", 3, 60),      # 3 password reset requests per min
        ("/chat", 25, 60),            # 25 AI queries per min
    ]
    DEFAULT_LIMIT: Tuple[int, int] = (150, 60)  # 150 requests per min for other endpoints

    def __init__(self, app):
        super().__init__(app)
        self.requests_log: Dict[str, List[float]] = defaultdict(list)

    def _get_limit(self, path: str) -> Tuple[int, int]:
        for prefix, max_req, window in self.ROUTE_LIMITS:
            if path.startswith(prefix):
                return max_req, window
        return self.DEFAULT_LIMIT

    async def dispatch(self, request: Request, call_next):
        # Skip static assets
        if request.url.path.startswith("/ui") or request.method == "OPTIONS":
            return await call_next(request)

        # Get client IP (support X-Forwarded-For if behind reverse proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "127.0.0.1")

        max_req, window = self._get_limit(request.url.path)
        key = f"{client_ip}:{request.url.path}"
        now = time.time()
        cutoff = now - window

        # Purge expired timestamps for this key
        timestamps = [t for t in self.requests_log[key] if t > cutoff]
        self.requests_log[key] = timestamps

        if len(timestamps) >= max_req:
            retry_after = int(window - (now - timestamps[0])) if timestamps else window
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Too many requests. Rate limit is {max_req} requests per {window}s. Please wait.",
                    "retry_after": max(1, retry_after)
                },
                headers={"Retry-After": str(max(1, retry_after))}
            )

        self.requests_log[key].append(now)
        return await call_next(request)
