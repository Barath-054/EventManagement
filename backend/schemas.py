from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import datetime

# --- Authentication & User Schemas ---
class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: Optional[str] = "customer"
    organization_name: Optional[str] = None
    preferred_locality: Optional[str] = "RS Puram"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    preferred_locality: Optional[str] = "RS Puram"
    organization_name: Optional[str] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- Category Schemas ---
class EventTypeOut(BaseModel):
    id: int
    category_id: int
    name: str
    name_tamil: Optional[str] = None
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class EventTypeCreate(BaseModel):
    name: str
    name_tamil: Optional[str] = None
    description: Optional[str] = None

class EventCategoryOut(BaseModel):
    id: int
    code: str
    name: str
    name_tamil: Optional[str] = None
    description: Optional[str] = None
    icon: str
    display_order: int
    is_active: bool
    event_types: List[EventTypeOut] = []

    class Config:
        from_attributes = True

class EventCategoryCreate(BaseModel):
    code: str
    name: str
    name_tamil: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = "calendar"
    display_order: Optional[int] = 0
    event_types: Optional[List[str]] = []

# --- Service Schemas ---
class ServiceOut(BaseModel):
    id: int
    service_category_id: int
    category_name: Optional[str] = ""
    code: str
    name: str
    description: Optional[str] = None
    unit_type: str
    base_price: float
    min_quantity: int
    eligible_categories: List[str] = []
    is_mandatory: bool
    is_active: bool

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    service_category_id: int
    code: str
    name: str
    description: Optional[str] = None
    unit_type: str = "per_event"
    base_price: float
    min_quantity: Optional[int] = 1
    eligible_categories: Optional[List[str]] = ["*"]
    is_mandatory: Optional[bool] = False

# --- Package Schemas ---
class PackageServiceItem(BaseModel):
    service_id: int
    service_name: str
    unit_type: str
    unit_price: float
    included_quantity: float
    is_customizable: bool

class EventPackageOut(BaseModel):
    id: int
    category_id: int
    category_code: Optional[str] = None
    tier: str
    name: str
    description: Optional[str] = None
    base_price: float
    attendee_limit: int
    is_active: bool
    included_services: List[PackageServiceItem] = []

    class Config:
        from_attributes = True

class EventPackageCreate(BaseModel):
    category_id: int
    tier: str
    name: str
    description: Optional[str] = None
    base_price: float
    attendee_limit: int
    service_ids: Optional[List[int]] = []

# --- Event Schemas ---
class ServiceSelection(BaseModel):
    service_id: int
    quantity: float
    notes: Optional[str] = None

class EventCreateRequest(BaseModel):
    category_id: int
    event_type_id: Optional[int] = None
    title: str
    event_date: str
    start_time: Optional[str] = "09:00"
    end_time: Optional[str] = "18:00"
    expected_attendees: int = 50
    budget: float = 50000.0
    venue_type: str = "hotel_banquet"
    preferred_locality: str = "RS Puram"
    venue_address: Optional[str] = None
    indoor_outdoor: str = "indoor"
    theme: Optional[str] = None
    is_custom: Optional[bool] = False
    
    # Category-specific dynamic requirement fields
    form_data: Optional[Dict[str, Any]] = {}
    special_instructions: Optional[str] = None
    tradition_notes: Optional[str] = None
    dietary_preferences: Optional[str] = "mixed"
    av_requirements: Optional[str] = None
    stage_requirements: Optional[str] = None
    accessibility_notes: Optional[str] = None
    
    # Initial Package or Services
    package_id: Optional[int] = None
    services: Optional[List[ServiceSelection]] = []

class EventUpdateRequest(BaseModel):
    title: Optional[str] = None
    event_date: Optional[str] = None
    expected_attendees: Optional[int] = None
    budget: Optional[float] = None
    venue_type: Optional[str] = None
    preferred_locality: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    services: Optional[List[ServiceSelection]] = None

class EventOut(BaseModel):
    id: int
    user_id: int
    category_id: int
    category_name: Optional[str] = None
    category_code: Optional[str] = None
    event_type_id: Optional[int] = None
    event_type_name: Optional[str] = None
    title: str
    event_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    expected_attendees: int
    budget: float
    venue_type: str
    preferred_locality: str
    venue_address: Optional[str] = None
    indoor_outdoor: str
    theme: Optional[str] = None
    status: str
    is_custom: bool
    created_at: datetime.datetime
    
    form_data: Optional[Dict[str, Any]] = {}
    special_instructions: Optional[str] = None
    tradition_notes: Optional[str] = None
    dietary_preferences: Optional[str] = None

    class Config:
        from_attributes = True

# --- Quotation & Pricing Schemas ---
class QuotationItemOut(BaseModel):
    id: int
    service_id: Optional[int] = None
    service_name: str
    category_name: str
    unit_type: str
    quantity: float
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class QuotationOut(BaseModel):
    id: int
    quotation_number: str
    event_id: int
    event_title: Optional[str] = None
    category_name: Optional[str] = None
    version: int
    subtotal: float
    tax_rate: float
    tax_amount: float
    discount_amount: float
    grand_total: float
    advance_required: float
    status: str
    valid_until: Optional[str] = None
    items: List[QuotationItemOut] = []
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class QuotationChangeRequest(BaseModel):
    reason: str
    modified_services: Optional[List[ServiceSelection]] = None

# --- Payment Schemas ---
class PaymentRequest(BaseModel):
    quotation_id: int
    payment_type: str = "advance"  # advance, balance, full
    payment_method: str = "upi"  # upi, card, netbanking
    card_number: Optional[str] = None
    upi_id: Optional[str] = None

class PaymentOut(BaseModel):
    id: int
    quotation_id: int
    transaction_reference: str
    payment_type: str
    payment_method: str
    amount: float
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Booking & Task Schemas ---
class EventTaskOut(BaseModel):
    id: int
    title: str
    category: str
    status: str
    assigned_to: str
    due_date: Optional[str] = None
    completed_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class BookingOut(BaseModel):
    id: int
    booking_reference: str
    quotation_id: int
    event_id: int
    event_title: Optional[str] = None
    category_name: Optional[str] = None
    status: str
    advance_paid: float
    balance_due: float
    confirmed_at: datetime.datetime
    tasks: List[EventTaskOut] = []

    class Config:
        from_attributes = True

# --- Review Schemas ---
class ReviewCreate(BaseModel):
    event_id: int
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    feedback_text: str

class ReviewOut(BaseModel):
    id: int
    event_id: int
    user_name: str
    rating: int
    title: Optional[str] = None
    feedback_text: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- AI Recommendation Schemas ---
class RecommendationOut(BaseModel):
    service_id: int
    service_name: str
    service_code: str
    category_name: str
    unit_type: str
    suggested_quantity: float
    unit_price: float
    estimated_cost: float
    priority: str  # Essential, Highly Recommended, Optional Upgrade
    reason: str

class AIAnalysisResponse(BaseModel):
    feasibility_score: float
    feasibility_status: str
    budget_allocated: float
    estimated_total: float
    difference: float
    is_within_budget: bool
    explanation: str
    recommendations: List[RecommendationOut]
    cost_saving_tips: List[str]
    coimbatore_venue_advice: str
