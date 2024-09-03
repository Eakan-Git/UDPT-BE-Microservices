from fastapi import Request
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from models.redis import get_redis_value

from config import SECRET_KEY, ALGORITHM

class VerifyTokenMiddleware(BaseHTTPMiddleware):
    EXCLUDE_PATHS = [
        "",
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/favicon.ico",
    ]

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response

        if request.url.path in self.EXCLUDE_PATHS:
            response = await call_next(request)
            return response
        
        token = request.headers.get("Authorization")
        token = token.split("Bearer ")[-1] if token else None
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username_from_given_token = payload.get("username")
                redis_username = get_redis_value(token)
                if redis_username is None:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Token not found in redis"},
                    )
                if redis_username != username_from_given_token:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": 'Username mismatch from saved token.'},
                    )
                
                request.state.user = payload
            except jwt.JWTError:
                print("JWT decoding error at middleware")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token"},
                )
        else:
            return JSONResponse(
                status_code=403,
                content={"detail": "Authorization header missing"},
            )
        
        response = await call_next(request)
        return response