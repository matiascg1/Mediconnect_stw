from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx
import logging
from typing import Optional

from backend.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Service URLs
AUTH_SERVICE_URL = f"http://localhost:{settings.AUTH_SERVICE_PORT}"
USER_SERVICE_URL = f"http://localhost:{settings.USER_SERVICE_PORT}"
APPOINTMENT_SERVICE_URL = f"http://localhost:{settings.APPOINTMENT_SERVICE_PORT}"
EHR_SERVICE_URL = f"http://localhost:{settings.EHR_SERVICE_PORT}"
PRESCRIPTION_SERVICE_URL = f"http://localhost:{settings.PRESCRIPTION_SERVICE_PORT}"

async def validate_token(authorization: Optional[str] = Header(None)):
    """Validate JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/v1/auth/validate-token",
                json={"token": token},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

# Auth routes
@router.post("/auth/register")
async def register_user(request: dict):
    """Register user through auth service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/v1/auth/register",
                json=request,
                timeout=10.0
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Auth service error: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")

@router.post("/auth/login")
async def login_user(request: dict):
    """Login user through auth service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/v1/auth/login",
                json=request,
                timeout=10.0
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Auth service error: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")

# User routes
@router.get("/users/me")
async def get_current_user(token_data: dict = Depends(validate_token)):
    """Get current user info"""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token_data['payload']['sub']}"}
            response = await client.get(
                f"{USER_SERVICE_URL}/api/v1/users/me",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"User service error: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")

# Appointment routes
@router.get("/appointments")
async def get_appointments(token_data: dict = Depends(validate_token)):
    """Get user appointments"""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token_data['payload']['sub']}"}
            response = await client.get(
                f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments",
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Appointment service error: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")

@router.post("/appointments")
async def create_appointment(request: dict, token_data: dict = Depends(validate_token)):
    """Create new appointment"""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token_data['payload']['sub']}"}
            response = await client.post(
                f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments",
                json=request,
                headers=headers,
                timeout=10.0
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            logger.error(f"Appointment service error: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")
