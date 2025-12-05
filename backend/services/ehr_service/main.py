from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.config.settings import settings
from backend.services.ehr_service.handlers import router as ehr_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EHR Service",
    description="Electronic Health Records Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ehr_router, prefix="/api/v1/ehr", tags=["ehr"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ehr"}

if __name__ == "__main__":
    logger.info(f"Starting EHR Service on port {settings.EHR_SERVICE_PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.EHR_SERVICE_PORT,
        reload=True
    )
