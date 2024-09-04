from mangum import Mangum
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from middleware.auth_middleware import VerifyTokenMiddleware

from views.v1.voucher_exchange_view import router as voucher_exchange_router

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

app.title = "Voucher exchange service for UDPT project"
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

app.include_router(voucher_exchange_router, prefix="/api/v1", tags=["Voucher exchange v1"])

handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    uvicorn.run("main:app", host=host, port=port, reload=True)