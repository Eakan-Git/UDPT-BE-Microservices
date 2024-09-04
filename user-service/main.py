import asyncio
from mangum import Mangum
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from rabbitmq.auth_rpc_server import AuthRPCServer
from rabbitmq.get_user_rpc_server import GetUserRPCServer

from middleware.auth_middleware import VerifyTokenMiddleware
from views.v1.user_view import router as user_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(VerifyTokenMiddleware)

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

app.title = "User service for UDPT project"
app.description = "API for UDPT project"
app.version = "0.1.0"

@app.get("/")
async def root():
    return HTMLResponse(html)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(status_code=200)

app.include_router(user_router, prefix="/api/v1", tags=["User v1"])

handler = Mangum(app, lifespan="off")

async def start_rpc_server():
    auth_server = AuthRPCServer()
    await auth_server.setup()
    asyncio.create_task(auth_server.start())

    get_user_server = GetUserRPCServer()
    await get_user_server.setup()
    asyncio.create_task(get_user_server.start())
    return auth_server, get_user_server

@app.on_event("startup")
async def startup_event():
    await start_rpc_server()

if __name__ == "__main__":
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run("main:app", host=host, port=port, reload=True)