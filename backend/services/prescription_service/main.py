from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.config.settings import settings
from backend.services.prescription_service.handlers import router as prescription_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Prescription Service",
    description="Prescription Management Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prescription_router, prefix="/api/v1/prescriptions", tags=["prescriptions"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "prescription"}

if __name__ == "__main__":
    logger.info(f"Starting Prescription Service on port {settings.PRESCRIPTION_SERVICE_PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PRESCRIPTION_SERVICE_PORT,
        reload=True
    )
