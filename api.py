from fastapi import FastAPI
from routers import conversations,messages
from fastapi.responses import JSONResponse
from exceptions import AIServiceError

app = FastAPI()
app.include_router(conversations.router)
app.include_router(messages.router)

@app.exception_handler(AIServiceError)
async def ai_service_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail":"AI service failed"},
    )