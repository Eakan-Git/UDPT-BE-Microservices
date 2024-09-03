from fastapi import FastAPI, Response
from fastapi import HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

from middleware.auth_middleware import VerifyTokenMiddleware

from views.v1.auth_view import router as auth_router

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI</title>
    </head>
    <body>
        <div class="bg-gray-200 p-4 rounded-lg shadow-lg">
            <h1>FastAPI UDPT</h1>
            <ul>
                <li><a href="/docs">/docs</a></li>
                <li><a href="/redoc">/redoc</a></li>
            </ul>
        </div>
    </body>
</html>
"""

load_dotenv()

app = FastAPI()

app.title = "Gateway for UDPT project"
app.description = "Gateway for UDPT project"
app.version = "0.1.0"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(VerifyTokenMiddleware)

app.include_router(auth_router, prefix="/api/v1", tags=["Auth v1"])

@app.get("/")
async def root():
    return HTMLResponse(html)

@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(status_code=200)

if __name__ == "__main__":
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run("main:app", host=host, port=port, reload=True)