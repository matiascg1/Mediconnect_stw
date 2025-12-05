from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from backend.services.ehr_service.service import EHRService

router = APIRouter()

class EHRCreateRequest(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    consultation_date: datetime
    symptoms: str
    diagnosis: str
    treatment_plan: str
    prescription_id: Optional[int] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None

class EHRUpdateRequest(BaseModel):
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescription_id: Optional[int] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None

# Placeholder auth dependency
async def get_current_user():
    return {"user_id": 1, "role": "doctor"}

@router.post("/")
async def create_ehr_record(
    request: EHRCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new EHR record"""
    result = await EHRService.create_ehr_record(request.dict())
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result["error"]
        )
    
    return result

@router.get("/{ehr_id}")
async def get_ehr_record(ehr_id: int):
    """Get EHR record by ID"""
    ehr_record = await EHRService.get_ehr_by_id(ehr_id)
    if not ehr_record:
        raise HTTPException(status_code=404, detail="EHR record not found")
    return ehr_record

@router.get("/patient/{patient_id}")
async def get_patient_ehr_history(
    patient_id: int,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all EHR records for a patient"""
    ehr_records = await EHRService.get_patient_ehr_history(patient_id, limit)
    return {"records": ehr_records, "count": len(ehr_records)}

@router.get("/doctor/{doctor_id}")
async def get_doctor_ehr_records(
    doctor_id: int,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all EHR records created by a doctor"""
    ehr_records = await EHRService.get_doctor_ehr_records(doctor_id, limit)
    return {"records": ehr_records, "count": len(ehr_records)}

@router.put("/{ehr_id}")
async def update_ehr_record(
    ehr_id: int,
    update_data: EHRUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update EHR record"""
    result = await EHRService.update_ehr_record(
        ehr_id, 
        update_data.dict(exclude_unset=True)
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result["error"]
        )
    
    return result

@router.get("/search/")
async def search_ehr_records(
    patient_id: Optional[int] = Query(None),
    doctor_id: Optional[int] = Query(None),
    diagnosis: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Search EHR records with filters"""
    start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    ehr_records = await EHRService.search_ehr_records(
        patient_id, doctor_id, diagnosis, start_datetime, end_datetime
    )
    return {"records": ehr_records, "count": len(ehr_records)}

@router.get("/patient/{patient_id}/statistics")
async def get_patient_statistics(patient_id: int):
    """Get statistics for a patient"""
    statistics = await EHRService.get_patient_statistics(patient_id)
    return statistics
