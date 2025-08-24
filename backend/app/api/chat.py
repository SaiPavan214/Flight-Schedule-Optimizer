from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import pandas as pd
from ..database import get_db
from ..schemas import ChatMessage, ChatResponse
from ..services.gemini_service import gemini_service
from ..services.data_service import data_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """Send a message to the AI chatbot"""
    try:
        # First, try to get a response from the data service based on the CSV data
        csv_response = data_service.get_chat_response(message.message)
        
        if csv_response:
            return ChatResponse(
                response=csv_response,
                confidence=0.95,
                sources=["flight_data_csv"]
            )
        
        # Fallback to Gemini AI if no CSV-based response
        response = await gemini_service.generate_chatbot_response(
            message.message, 
            message.context
        )
        return ChatResponse(**response)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat message: {str(e)}"
        )

@router.get("/health", response_model=dict)
async def chat_health_check():
    """Check if the chat service is healthy"""
    try:
        # Test basic functionality
        test_response = await gemini_service.generate_chatbot_response(
            "Hello", 
            "Health check"
        )
        return {
            "status": "healthy",
            "service": "chat",
            "ai_model": "gemini-pro",
            "response_time": "normal",
            "data_source": "flight_data.csv"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Chat service unhealthy: {str(e)}"
        )

@router.get("/dashboard/flights", response_model=dict)
async def get_dashboard_flights():
    """Fetch flight data for the dashboard"""
    try:
        # Get recent flights from the data service
        recent_flights = data_service.get_recent_flights(hours=24)
        flight_stats = data_service.get_flight_statistics()
        
        return JSONResponse(content={
            "flights": recent_flights,
            "statistics": flight_stats
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading flight data: {str(e)}"
        )

@router.get("/test/data", response_model=dict)
async def test_data_service():
    """Test endpoint to verify data service is working"""
    try:
        # Test basic data service functionality
        all_flights = data_service.get_all_flights()
        stats = data_service.get_flight_statistics()
        alerts = data_service.get_alerts()
        
        return {
            "status": "success",
            "total_flights": len(all_flights),
            "statistics": stats,
            "total_alerts": len(alerts),
            "sample_flight": all_flights[0] if all_flights else None,
            "data_loaded": not data_service.data.empty
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data_loaded": not data_service.data.empty
        }
