from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models import Alert, AlertType
from ..schemas import AlertCreate, AlertUpdate

class AlertService:
    
    @staticmethod
    def create_alert(db: Session, alert: AlertCreate) -> Alert:
        """Create a new alert"""
        db_alert = Alert(**alert.dict())
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    @staticmethod
    def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """Get an alert by ID"""
        return db.query(Alert).filter(Alert.id == alert_id).first()
    
    @staticmethod
    def get_alerts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        alert_type: Optional[AlertType] = None,
        resolved: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Alert]:
        """Get alerts with optional filters"""
        query = db.query(Alert)
        
        if alert_type:
            query = query.filter(Alert.type == alert_type)
        
        if resolved is not None:
            query = query.filter(Alert.resolved == resolved)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                and_(
                    Alert.title.ilike(search_term),
                    Alert.message.ilike(search_term)
                )
            )
        
        return query.order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_alert(db: Session, alert_id: int, alert_update: AlertUpdate) -> Optional[Alert]:
        """Update an alert"""
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            return None
        
        update_data = alert_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_alert, field, value)
        
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    @staticmethod
    def resolve_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """Mark an alert as resolved"""
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            return None
        
        db_alert.resolved = True
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    @staticmethod
    def delete_alert(db: Session, alert_id: int) -> bool:
        """Delete an alert"""
        db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not db_alert:
            return False
        
        db.delete(db_alert)
        db.commit()
        return True
    
    @staticmethod
    def get_active_alerts(db: Session) -> List[Alert]:
        """Get all unresolved alerts"""
        return db.query(Alert).filter(Alert.resolved == False).order_by(Alert.timestamp.desc()).all()
    
    @staticmethod
    def get_critical_alerts(db: Session) -> List[Alert]:
        """Get all critical unresolved alerts"""
        return db.query(Alert).filter(
            and_(
                Alert.type == AlertType.CRITICAL,
                Alert.resolved == False
            )
        ).order_by(Alert.timestamp.desc()).all()
    
    @staticmethod
    def get_recent_alerts(db: Session, hours: int = 24) -> List[Alert]:
        """Get alerts from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return db.query(Alert).filter(Alert.timestamp >= cutoff_time).order_by(Alert.timestamp.desc()).all()
    
    @staticmethod
    def get_alert_statistics(db: Session) -> Dict[str, Any]:
        """Get alert statistics"""
        total_alerts = db.query(Alert).count()
        active_alerts = db.query(Alert).filter(Alert.resolved == False).count()
        
        # Type distribution
        type_counts = db.query(
            Alert.type,
            func.count(Alert.id).label('count')
        ).group_by(Alert.type).all()
        
        # Critical alerts
        critical_count = db.query(Alert).filter(
            and_(
                Alert.type == AlertType.CRITICAL,
                Alert.resolved == False
            )
        ).count()
        
        # Recent alerts (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_alerts = db.query(Alert).filter(Alert.timestamp >= yesterday).count()
        
        # Resolution time (average for resolved alerts)
        resolved_alerts = db.query(Alert).filter(Alert.resolved == True).all()
        if resolved_alerts:
            total_resolution_time = sum(
                (alert.updated_at - alert.timestamp).total_seconds() 
                for alert in resolved_alerts 
                if alert.updated_at
            )
            avg_resolution_time = total_resolution_time / len(resolved_alerts) / 60  # in minutes
        else:
            avg_resolution_time = 0
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "critical_alerts": critical_count,
            "recent_alerts": recent_alerts,
            "avg_resolution_time_minutes": round(avg_resolution_time, 1),
            "type_distribution": {alert_type: count for alert_type, count in type_counts}
        }
    
    @staticmethod
    def create_system_alert(
        db: Session,
        alert_type: AlertType,
        title: str,
        message: str
    ) -> Alert:
        """Create a system-generated alert"""
        alert_data = AlertCreate(
            type=alert_type,
            title=title,
            message=message,
            resolved=False
        )
        return AlertService.create_alert(db, alert_data)
    
    @staticmethod
    def cleanup_old_alerts(db: Session, days: int = 30) -> int:
        """Delete alerts older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = db.query(Alert).filter(Alert.timestamp < cutoff_date).delete()
        db.commit()
        return deleted_count
