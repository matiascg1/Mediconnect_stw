from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from backend.services.prescription_service.service import PrescriptionService

router = APIRouter()

class PrescriptionCreateRequest(BaseModel):
    patient_id: int
    doctor_id: int
    ehr_id: Optional[int] = None
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int
    instructions: Optional[str] = None
    prescribed_date: Optional[datetime] = None
    status: str = "active"
    refills_remaining: int = 0

class PrescriptionUpdateRequest(BaseModel):
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    instructions: Optional[str] = None
    status: Optional[str] = None
    refills_remaining: Optional[int] = None

# Placeholder auth dependency
async def get_current_user():
    return {"user_id": 1, "role": "doctor"}

@router.post("/")
async def create_prescription(
    request: PrescriptionCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new prescription"""
    result = await PrescriptionService.create_prescription(request.dict())
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result["error"]
        )
    
    return result

@router.get("/{prescription_id}")
async def get_prescription(prescription_id: int):
    """Get prescription by ID"""
    prescription = await PrescriptionService.get_prescription_by_id(prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.get("/patient/{patient_id}")
async def get_patient_prescriptions(
    patient_id: int,
    status: Optional[str] = Query(None)
):
    """Get all prescriptions for a patient"""
    prescriptions = await PrescriptionService.get_patient_prescriptions(patient_id, status)
    return {"prescriptions": prescriptions, "count": len(prescriptions)}

@router.get("/doctor/{doctor_id}")
async def get_doctor_prescriptions(
    doctor_id: int,
    status: Optional[str] = Query(None)
):
    """Get all prescriptions created by a doctor"""
    prescriptions = await PrescriptionService.get_doctor_prescriptions(doctor_id, status)
    return {"prescriptions": prescriptions, "count": len(prescriptions)}

@router.put("/{prescription_id}")
async def update_prescription(
    prescription_id: int,
    update_data: PrescriptionUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update prescription"""
    result = await PrescriptionService.update_prescription(
        prescription_id, 
        update_data.dict(exclude_unset=True)
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result["error"]
        )
    
    return result

@router.post("/{prescription_id}/refill")
async def refill_prescription(
    prescription_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Refill a prescription"""
    result = await PrescriptionService.refill_prescription(prescription_id)
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result["error"]
        )
    
    return result

@router.get("/patient/{patient_id}/active")
async def get_active_prescriptions(patient_id: int):
    """Get active prescriptions for a patient"""
    prescriptions = await PrescriptionService.get_active_prescriptions(patient_id)
    return {"prescriptions": prescriptions, "count": len(prescriptions)}

@router.get("/search/")
async def search_prescriptions(
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    medication_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Search prescriptions with filters"""
    prescriptions = await PrescriptionService.search_prescriptions(
        patient_id, doctor_id, medication_name, status
    )
    return {"prescriptions": prescriptions, "count": len(prescriptions)}
