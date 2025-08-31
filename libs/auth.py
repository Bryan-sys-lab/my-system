from fastapi import Body, Header, HTTPException
import os
import logging

logger = logging.getLogger("libs.auth")

try:
    import jwt
    _HAS_JWT = True
except Exception:
    _HAS_JWT = False


def require_run_all_auth(secret: str | None = Body(None, embed=True), authorization: str | None = Header(None)) -> bool:
    """Pluggable auth dependency for run_all endpoints.

    Accepts either a body `secret` (keeps compatibility with existing tests) or
    a Bearer JWT in Authorization header. The JWT uses HS256 with the same
    RUN_ALL_SECRET env var as the key if present.
    """
    expected = os.getenv("RUN_ALL_SECRET")
    if expected and secret and secret == expected:
        logger.info("run_all auth: accepted via body secret")
        return True

    # try JWT Bearer token
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(None, 1)[1]
        if not _HAS_JWT:
            logger.warning("JWT auth requested but PyJWT not available")
            raise HTTPException(status_code=403, detail="JWT auth not available")
        if not expected:
            raise HTTPException(status_code=403, detail="server has no RUN_ALL_SECRET configured for JWT validation")
        try:
            payload = jwt.decode(token, expected, algorithms=["HS256"])
            logger.info("run_all auth: accepted via JWT")
            return True
        except Exception as e:
            logger.warning("JWT decode failed: %s", e)
            raise HTTPException(status_code=403, detail="invalid token")

    raise HTTPException(status_code=403, detail="run_all is disabled or invalid credentials")
