from mangum import Mangum
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import asyncio
from dotenv import load_dotenv
from rabbitmq.get_voucher_rpc_server import GetVoucherRPCServer

from middleware.auth_middleware import VerifyTokenMiddleware

from views.v1.voucher_view import router as voucher_router

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

app.title = "Voucher service for UDPT project"
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

app.include_router(voucher_router, prefix="/api/v1", tags=["Voucher v1"])

handler = Mangum(app, lifespan="off")

async def start_rpc_server():
    get_voucher_rpc_server = GetVoucherRPCServer()
    await get_voucher_rpc_server.setup()
    asyncio.create_task(get_voucher_rpc_server.start())
    return get_voucher_rpc_server

@app.on_event("startup")
async def startup_event():
    await start_rpc_server()

if __name__ == "__main__":
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run("main:app", host=host, port=port, reload=True)