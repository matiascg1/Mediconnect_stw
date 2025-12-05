from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from backend.services.admin_service.service import AdminService

router = APIRouter()

# Placeholder auth dependency - only admin
async def verify_admin():
    # In real implementation, check JWT token for admin role
    return {"user_id": 1, "role": "admin"}

@router.get("/stats")
async def get_system_stats(admin: dict = Depends(verify_admin)):
    """Get system statistics"""
    stats = await AdminService.get_system_stats()
    return stats

@router.get("/metrics/daily")
async def get_daily_metrics(
    days: int = Query(7, ge=1, le=365),
    admin: dict = Depends(verify_admin)
):
    """Get daily metrics"""
    metrics = await AdminService.get_daily_metrics(days)
    return {"metrics": metrics, "days": days}

@router.get("/user/{user_id}/activity")
async def get_user_activity(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    admin: dict = Depends(verify_admin)
):
    """Get user activity history"""
    activity = await AdminService.get_user_activity(user_id, days)
    
    if "error" in activity:
        raise HTTPException(status_code=404, detail=activity["error"])
    
    return activity

@router.get("/logs")
async def get_system_logs(
    log_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    admin: dict = Depends(verify_admin)
):
    """Get system logs"""
    start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    logs = await AdminService.get_system_logs(log_type, start_datetime, end_datetime, limit)
    return {"logs": logs, "count": len(logs)}

@router.post("/backup")
async def trigger_backup(admin: dict = Depends(verify_admin)):
    """Trigger database backup"""
    result = await AdminService.backup_database()
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status_code", 500),
            detail=result["error"]
        )
    
    return result

@router.get("/health")
async def get_system_health(admin: dict = Depends(verify_admin)):
    """Check system health"""
    health = await AdminService.get_system_health()
    return health
