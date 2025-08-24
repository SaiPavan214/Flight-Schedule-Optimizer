from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import Alert, AlertCreate, AlertUpdate, APIResponse
from ..services.alert_service import AlertService
from ..services.data_service import data_service
from ..models import AlertType

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=List[dict])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_type: Optional[str] = None,
    resolved: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alerts with optional filters"""
    try:
        # Get alerts from data service
        alerts = data_service.get_alerts()
        
        # Apply filters
        if alert_type:
            alerts = [a for a in alerts if a.get('type') == alert_type]
        if resolved is not None:
            alerts = [a for a in alerts if a.get('resolved') == resolved]
        if search:
            search_lower = search.lower()
            alerts = [a for a in alerts if 
                     search_lower in a.get('title', '').lower() or 
                     search_lower in a.get('message', '').lower()]
        
        # Apply pagination
        total_alerts = len(alerts)
        alerts = alerts[skip:skip + limit]
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.get("/active/all", response_model=List[dict])
async def get_active_alerts(db: Session = Depends(get_db)):
    """Get all unresolved alerts"""
    try:
        alerts = data_service.get_alerts()
        active_alerts = [a for a in alerts if not a.get('resolved', False)]
        return active_alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active alerts: {str(e)}")

@router.get("/critical/all", response_model=List[dict])
async def get_critical_alerts(db: Session = Depends(get_db)):
    """Get all critical unresolved alerts"""
    try:
        alerts = data_service.get_alerts()
        critical_alerts = [a for a in alerts if a.get('type') == 'critical' and not a.get('resolved', False)]
        return critical_alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching critical alerts: {str(e)}")

@router.get("/statistics/overview", response_model=dict)
async def get_alert_statistics(db: Session = Depends(get_db)):
    """Get alert statistics"""
    try:
        alerts = data_service.get_alerts()
        
        total_alerts = len(alerts)
        critical_count = len([a for a in alerts if a.get('type') == 'critical'])
        warning_count = len([a for a in alerts if a.get('type') == 'warning'])
        info_count = len([a for a in alerts if a.get('type') == 'info'])
        resolved_count = len([a for a in alerts if a.get('resolved', False)])
        
        return {
            "total_alerts": total_alerts,
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "info_alerts": info_count,
            "resolved_alerts": resolved_count,
            "active_alerts": total_alerts - resolved_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alert statistics: {str(e)}")

@router.get("/recent/{hours}", response_model=List[dict])
async def get_recent_alerts(
    hours: int,
    db: Session = Depends(get_db)
):
    """Get alerts from the last N hours"""
    try:
        from datetime import datetime, timedelta
        
        alerts = data_service.get_alerts()
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = []
        for alert in alerts:
            try:
                alert_time = datetime.fromisoformat(alert.get('timestamp', '').replace('Z', '+00:00'))
                if alert_time >= cutoff_time:
                    recent_alerts.append(alert)
            except:
                continue
        
        return recent_alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent alerts: {str(e)}")

@router.post("/{alert_id}/resolve", response_model=dict)
async def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    """Mark an alert as resolved"""
    try:
        # In a real system, you would update the database
        # For now, we'll return a success message
        return {
            "success": True,
            "message": f"Alert {alert_id} marked as resolved",
            "alert_id": alert_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving alert: {str(e)}")
