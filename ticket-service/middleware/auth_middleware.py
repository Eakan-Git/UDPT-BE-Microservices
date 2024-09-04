from fastapi import Request
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import SECRET_KEY, ALGORITHM

class VerifyTokenMiddleware(BaseHTTPMiddleware):
    EXCLUDE_PATHS = [
        "",
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
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
                request_state_user = {
                    "username": payload.get("username"),
                    "user_id": payload.get("user_id"),
                    "role": payload.get("role"),
                }
                request.state.user = request_state_user

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