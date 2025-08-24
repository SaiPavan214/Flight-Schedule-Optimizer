from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models import RunwayMetric
from ..schemas import RunwayMetricCreate, RunwayMetricUpdate
from .gemini_service import gemini_service

class RunwayService:
    
    @staticmethod
    def create_runway_metric(db: Session, metric: RunwayMetricCreate) -> RunwayMetric:
        """Create a new runway metric"""
        db_metric = RunwayMetric(**metric.dict())
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric
    
    @staticmethod
    def get_runway_metric(db: Session, metric_id: int) -> Optional[RunwayMetric]:
        """Get a runway metric by ID"""
        return db.query(RunwayMetric).filter(RunwayMetric.id == metric_id).first()
    
    @staticmethod
    def get_runway_metrics(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        runway: Optional[str] = None,
        hours: Optional[int] = None
    ) -> List[RunwayMetric]:
        """Get runway metrics with optional filters"""
        query = db.query(RunwayMetric)
        
        if runway:
            query = query.filter(RunwayMetric.runway == runway)
        
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            query = query.filter(RunwayMetric.timestamp >= cutoff_time)
        
        return query.order_by(RunwayMetric.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_runway_metric(db: Session, metric_id: int, metric_update: RunwayMetricUpdate) -> Optional[RunwayMetric]:
        """Update a runway metric"""
        db_metric = db.query(RunwayMetric).filter(RunwayMetric.id == metric_id).first()
        if not db_metric:
            return None
        
        update_data = metric_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_metric, field, value)
        
        db.commit()
        db.refresh(db_metric)
        return db_metric
    
    @staticmethod
    def delete_runway_metric(db: Session, metric_id: int) -> bool:
        """Delete a runway metric"""
        db_metric = db.query(RunwayMetric).filter(RunwayMetric.id == metric_id).first()
        if not db_metric:
            return False
        
        db.delete(db_metric)
        db.commit()
        return True
    
    @staticmethod
    def get_current_runway_status(db: Session) -> List[Dict[str, Any]]:
        """Get current status of all runways"""
        # Get the latest metric for each runway
        latest_metrics = db.query(RunwayMetric).distinct(RunwayMetric.runway).order_by(
            RunwayMetric.runway, RunwayMetric.timestamp.desc()
        ).all()
        
        status_list = []
        for metric in latest_metrics:
            # Calculate efficiency score
            efficiency = (metric.utilization / metric.capacity) * 100 if metric.capacity > 0 else 0
            
            # Determine status based on utilization and conflicts
            if metric.utilization > 90:
                status = "High Load"
            elif metric.utilization > 75:
                status = "Moderate Load"
            elif metric.utilization > 50:
                status = "Normal Load"
            else:
                status = "Low Load"
            
            if metric.conflicts > 5:
                status += " - Conflicts"
            
            status_list.append({
                "runway": metric.runway,
                "utilization": metric.utilization,
                "capacity": metric.capacity,
                "delays": metric.delays,
                "conflicts": metric.conflicts,
                "efficiency": round(efficiency, 1),
                "status": status,
                "timestamp": metric.timestamp
            })
        
        return status_list
    
    @staticmethod
    def get_runway_utilization_trends(db: Session, runway: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get utilization trends for a specific runway"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        metrics = db.query(RunwayMetric).filter(
            and_(
                RunwayMetric.runway == runway,
                RunwayMetric.timestamp >= cutoff_time
            )
        ).order_by(RunwayMetric.timestamp).all()
        
        trends = []
        for metric in metrics:
            efficiency = (metric.utilization / metric.capacity) * 100 if metric.capacity > 0 else 0
            trends.append({
                "timestamp": metric.timestamp,
                "utilization": metric.utilization,
                "efficiency": round(efficiency, 1),
                "delays": metric.delays,
                "conflicts": metric.conflicts
            })
        
        return trends
    
    @staticmethod
    def get_runway_statistics(db: Session) -> Dict[str, Any]:
        """Get comprehensive runway statistics"""
        # Get all runways
        runways = db.query(RunwayMetric.runway).distinct().all()
        runway_list = [r[0] for r in runways]
        
        # Calculate average utilization per runway
        avg_utilization = db.query(
            RunwayMetric.runway,
            func.avg(RunwayMetric.utilization).label('avg_utilization'),
            func.avg(RunwayMetric.delays).label('avg_delays'),
            func.avg(RunwayMetric.conflicts).label('avg_conflicts')
        ).group_by(RunwayMetric.runway).all()
        
        # Get current metrics
        current_status = RunwayService.get_current_runway_status(db)
        
        # Calculate overall statistics
        total_utilization = sum(status['utilization'] for status in current_status)
        total_capacity = sum(status['capacity'] for status in current_status)
        total_delays = sum(status['delays'] for status in current_status)
        total_conflicts = sum(status['conflicts'] for status in current_status)
        
        overall_efficiency = (total_utilization / total_capacity) * 100 if total_capacity > 0 else 0
        
        # Identify bottlenecks
        bottlenecks = [
            status for status in current_status 
            if status['utilization'] > 85 or status['conflicts'] > 3
        ]
        
        return {
            "total_runways": len(runway_list),
            "overall_efficiency": round(overall_efficiency, 1),
            "total_delays": total_delays,
            "total_conflicts": total_conflicts,
            "bottlenecks": bottlenecks,
            "runway_details": [
                {
                    "runway": runway,
                    "avg_utilization": round(avg_util, 1),
                    "avg_delays": round(avg_delays, 1),
                    "avg_conflicts": round(avg_conflicts, 1)
                }
                for runway, avg_util, avg_delays, avg_conflicts in avg_utilization
            ],
            "current_status": current_status
        }
    
    @staticmethod
    async def get_optimization_recommendations(db: Session) -> Dict[str, Any]:
        """Get AI-powered optimization recommendations"""
        # Get current runway status
        current_status = RunwayService.get_current_runway_status(db)
        
        # Get recent metrics for analysis
        recent_metrics = RunwayService.get_runway_metrics(db, hours=24)
        
        # Convert to format expected by Gemini
        runway_data = []
        for metric in recent_metrics:
            runway_data.append({
                "runway": metric.runway,
                "utilization": metric.utilization,
                "capacity": metric.capacity,
                "delays": metric.delays,
                "conflicts": metric.conflicts,
                "timestamp": metric.timestamp.isoformat()
            })
        
        # Get AI analysis
        try:
            analysis = await gemini_service.analyze_runway_optimization(runway_data)
            return analysis
        except Exception as e:
            print(f"Error getting optimization recommendations: {e}")
            return {
                "analysis": "Unable to analyze runway data at this time",
                "recommendations": [
                    {
                        "type": "immediate",
                        "action": "Monitor runway utilization patterns",
                        "impact": "Better understanding of traffic flow",
                        "priority": "medium"
                    }
                ],
                "efficiency_score": 75,
                "bottlenecks": ["Analysis temporarily unavailable"]
            }
    
    @staticmethod
    def get_peak_hours_analysis(db: Session, runway: str, days: int = 7) -> List[Dict[str, Any]]:
        """Analyze peak hours for a specific runway"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Get metrics grouped by hour
        hourly_data = db.query(
            func.extract('hour', RunwayMetric.timestamp).label('hour'),
            func.avg(RunwayMetric.utilization).label('avg_utilization'),
            func.avg(RunwayMetric.delays).label('avg_delays'),
            func.avg(RunwayMetric.conflicts).label('avg_conflicts'),
            func.count(RunwayMetric.id).label('data_points')
        ).filter(
            and_(
                RunwayMetric.runway == runway,
                RunwayMetric.timestamp >= cutoff_time
            )
        ).group_by(
            func.extract('hour', RunwayMetric.timestamp)
        ).order_by(
            func.extract('hour', RunwayMetric.timestamp)
        ).all()
        
        analysis = []
        for hour, avg_util, avg_delays, avg_conflicts, data_points in hourly_data:
            if data_points > 0:  # Only include hours with data
                analysis.append({
                    "hour": int(hour),
                    "avg_utilization": round(avg_util, 1),
                    "avg_delays": round(avg_delays, 1),
                    "avg_conflicts": round(avg_conflicts, 1),
                    "data_points": data_points,
                    "traffic_level": "High" if avg_util > 80 else "Medium" if avg_util > 50 else "Low"
                })
        
        return analysis
    
    @staticmethod
    def cleanup_old_metrics(db: Session, days: int = 30) -> int:
        """Delete metrics older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = db.query(RunwayMetric).filter(RunwayMetric.timestamp < cutoff_date).delete()
        db.commit()
        return deleted_count
