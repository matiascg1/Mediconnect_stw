from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.config.settings import settings
from backend.services.admin_service.handlers import router as admin_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Admin Service",
    description="Administration Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "admin"}

if __name__ == "__main__":
    logger.info(f"Starting Admin Service on port {settings.ADMIN_SERVICE_PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.ADMIN_SERVICE_PORT,
        reload=True
    )
