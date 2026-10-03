from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import conversations,messages
from fastapi.responses import JSONResponse
from exceptions import AIServiceError,AIServiceTimeoutError,AIServiceConnectionError
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://localhost:63342",
    # ],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(conversations.router)
app.include_router(messages.router)

@app.exception_handler(AIServiceTimeoutError)
async def ai_service_timeout_handler(request, exc):
    return JSONResponse(
        status_code=504,
        content={"detail":"AI service timeout"}
    )
@app.exception_handler(AIServiceConnectionError)
async def ai_service_connection_handler(request, exc):
    return JSONResponse(
        status_code=502,
        content={"detail":"AI service unavailable"}
    )
@app.exception_handler(AIServiceError)
async def ai_service_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail":"AI service failed"},
    )