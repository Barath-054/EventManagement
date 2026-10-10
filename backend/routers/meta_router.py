from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
from backend.database import get_db
from backend.config import settings
from backend.models import Vendor, Venue

router = APIRouter(prefix="/api/meta", tags=["Coimbatore Localization & Metadata"])

@router.get("/localities")
def get_localities():
    return {
        "city": settings.CITY,
        "state": settings.STATE,
        "localities": settings.COIMBATORE_LOCALITIES
    }

@router.get("/venue-types")
def get_venue_types():
    return {
        "city": settings.CITY,
        "venue_types": settings.COIMBATORE_VENUE_TYPES
    }

@router.get("/vendors")
def get_verified_vendors(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).filter(Vendor.is_verified == True).all()
    results = []
    for v in vendors:
        results.append({
            "id": v.id,
            "name": v.name,
            "business_name": v.business_name,
            "category": v.category,
            "locality": v.locality,
            "phone": v.phone,
            "email": v.email,
            "rating": v.rating,
            "sample_pricing_desc": v.sample_pricing_desc,
            "is_verified": v.is_verified
        })
    return results

@router.get("/venues")
def get_verified_venues(db: Session = Depends(get_db)):
    venues = db.query(Venue).filter(Venue.is_verified == True).all()
    results = []
    for v in venues:
        amenities = []
        try:
            amenities = json.loads(v.amenities_json) if v.amenities_json else []
        except Exception:
            pass
        results.append({
            "id": v.id,
            "name": v.name,
            "venue_type": v.venue_type,
            "locality": v.locality,
            "capacity": v.capacity,
            "base_day_rate": v.base_day_rate,
            "amenities": amenities,
            "is_verified": v.is_verified
        })
    return results
