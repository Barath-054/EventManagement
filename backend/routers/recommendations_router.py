from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models import Service, EventCategory
from backend.recommendation_ai import recommendation_ai
from backend.schemas import AIAnalysisResponse

router = APIRouter(prefix="/api/recommendations", tags=["AI Recommendations"])

class AIAnalysisRequest(BaseModel):
    category_id: Optional[int] = None
    category_code: Optional[str] = "wedding"
    attendees: int = 100
    budget: float = 100000.0
    venue_type: str = "hotel_banquet"
    preferred_locality: str = "RS Puram"
    indoor_outdoor: str = "indoor"
    form_data: Optional[Dict[str, Any]] = {}

@router.post("/analyze", response_model=AIAnalysisResponse)
def analyze_event(req: AIAnalysisRequest, db: Session = Depends(get_db)):
    cat_code = req.category_code
    if req.category_id:
        cat = db.query(EventCategory).filter(EventCategory.id == req.category_id).first()
        if cat:
            cat_code = cat.code

    # Fetch active services
    all_services = db.query(Service).filter(Service.is_active == True).all()
    services_list = []
    for s in all_services:
        services_list.append({
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "unit_type": s.unit_type,
            "base_price": s.base_price,
            "category_name": s.service_category.name if s.service_category else ""
        })

    result = recommendation_ai.generate_recommendations(
        category_code=cat_code,
        attendees=req.attendees,
        budget=req.budget,
        venue_type=req.venue_type,
        locality=req.preferred_locality,
        indoor_outdoor=req.indoor_outdoor,
        form_data=req.form_data or {},
        available_services=services_list
    )
    return result
