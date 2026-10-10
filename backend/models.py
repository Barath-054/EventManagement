import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="customer")  # customer, admin, vendor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    profile = relationship("CustomerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization_name = Column(String(200), nullable=True)
    address = Column(Text, nullable=True)
    preferred_locality = Column(String(100), default="Gandhipuram")
    gst_number = Column(String(30), nullable=True)
    notes = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="profile")

class EventCategory(Base):
    __tablename__ = "event_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # wedding, birthday, corporate, etc.
    name = Column(String(120), nullable=False)
    name_tamil = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="calendar")
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    event_types = relationship("EventType", back_populates="category", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="category")
    packages = relationship("EventPackage", back_populates="category", cascade="all, delete-orphan")

class EventType(Base):
    __tablename__ = "event_types"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("event_categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    name_tamil = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    category = relationship("EventCategory", back_populates="event_types")
    events = relationship("Event", back_populates="event_type")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("event_categories.id"), nullable=False)
    event_type_id = Column(Integer, ForeignKey("event_types.id"), nullable=True)
    title = Column(String(200), nullable=False)
    event_date = Column(String(30), nullable=True)
    start_time = Column(String(20), nullable=True)
    end_time = Column(String(20), nullable=True)
    expected_attendees = Column(Integer, default=50)
    budget = Column(Float, default=50000.0)
    venue_type = Column(String(80), default="hotel_banquet")
    preferred_locality = Column(String(100), default="RS Puram")
    venue_address = Column(Text, nullable=True)
    indoor_outdoor = Column(String(30), default="indoor")  # indoor, outdoor, both
    theme = Column(String(100), nullable=True)
    status = Column(String(40), default="draft")  # draft, submitted, quoted, approved, booked, executing, completed, cancelled
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="events")
    category = relationship("EventCategory", back_populates="events")
    event_type = relationship("EventType", back_populates="events")
    requirement = relationship("EventRequirement", back_populates="event", uselist=False, cascade="all, delete-orphan")
    selected_services = relationship("EventService", back_populates="event", cascade="all, delete-orphan")
    ai_recommendations = relationship("AIRecommendation", back_populates="event", cascade="all, delete-orphan")
    quotations = relationship("Quotation", back_populates="event", cascade="all, delete-orphan")
    booking = relationship("Booking", back_populates="event", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="event", cascade="all, delete-orphan")

class EventRequirement(Base):
    __tablename__ = "event_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), unique=True, nullable=False)
    # Flexible JSON storage for dynamic category-specific inputs
    form_data_json = Column(Text, default="{}")
    special_instructions = Column(Text, nullable=True)
    tradition_notes = Column(Text, nullable=True)
    dietary_preferences = Column(String(150), default="mixed")  # veg, non-veg, jain, mixed
    av_requirements = Column(Text, nullable=True)
    stage_requirements = Column(Text, nullable=True)
    accessibility_notes = Column(Text, nullable=True)
    
    event = relationship("Event", back_populates="requirement")

class ServiceCategory(Base):
    __tablename__ = "service_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    icon = Column(String(50), default="gear")
    display_order = Column(Integer, default=0)
    
    services = relationship("Service", back_populates="service_category", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    service_category_id = Column(Integer, ForeignKey("service_categories.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(60), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    # Unit types: per_person, per_hour, per_day, per_item, per_seat, per_event, per_worker
    unit_type = Column(String(40), default="per_event")
    base_price = Column(Float, default=1000.0)
    min_quantity = Column(Integer, default=1)
    eligible_categories_json = Column(Text, default="[]")  # List of category codes or ["*"]
    is_mandatory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    service_category = relationship("ServiceCategory", back_populates="services")
    package_inclusions = relationship("PackageService", back_populates="service", cascade="all, delete-orphan")
    event_services = relationship("EventService", back_populates="service")

class EventPackage(Base):
    __tablename__ = "event_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("event_categories.id", ondelete="CASCADE"), nullable=False)
    tier = Column(String(30), nullable=False)  # basic, standard, premium
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Float, default=25000.0)
    attendee_limit = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    
    category = relationship("EventCategory", back_populates="packages")
    package_services = relationship("PackageService", back_populates="package", cascade="all, delete-orphan")

class PackageService(Base):
    __tablename__ = "package_services"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("event_packages.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    included_quantity = Column(Float, default=1.0)
    is_customizable = Column(Boolean, default=True)
    
    package = relationship("EventPackage", back_populates="package_services")
    service = relationship("Service", back_populates="package_inclusions")

class EventService(Base):
    __tablename__ = "event_services"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    notes = Column(String(200), nullable=True)
    is_selected = Column(Boolean, default=True)
    
    event = relationship("Event", back_populates="selected_services")
    service = relationship("Service", back_populates="event_services")

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    recommendations_json = Column(Text, default="[]")
    cost_saving_alternatives_json = Column(Text, default="[]")
    feasibility_score = Column(Float, default=90.0)  # 0 to 100% budget fit
    explanation_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    event = relationship("Event", back_populates="ai_recommendations")

class Quotation(Base):
    __tablename__ = "quotations"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_number = Column(String(60), unique=True, index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, default=1)
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.18)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    advance_required = Column(Float, default=0.0)
    status = Column(String(30), default="pending")  # pending, approved, change_requested, rejected
    valid_until = Column(String(30), nullable=True)
    snapshot_data_json = Column(Text, default="{}")  # Immutable snapshot of services & prices
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    event = relationship("Event", back_populates="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    revisions = relationship("QuotationRevision", back_populates="quotation", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="quotation")
    booking = relationship("Booking", back_populates="quotation", uselist=False)

class QuotationItem(Base):
    __tablename__ = "quotation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    service_name = Column(String(150), nullable=False)
    category_name = Column(String(100), nullable=False)
    unit_type = Column(String(40), default="per_event")
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    
    quotation = relationship("Quotation", back_populates="items")

class QuotationRevision(Base):
    __tablename__ = "quotation_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    revision_number = Column(Integer, default=1)
    change_summary = Column(Text, nullable=False)
    requested_by = Column(String(100), default="customer")
    previous_total = Column(Float, default=0.0)
    revised_total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    quotation = relationship("Quotation", back_populates="revisions")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    transaction_reference = Column(String(80), unique=True, index=True, nullable=False)
    payment_type = Column(String(30), default="advance")  # advance, balance, full
    payment_method = Column(String(30), default="upi")  # upi, card, netbanking, cash
    amount = Column(Float, default=0.0)
    status = Column(String(30), default="completed")  # pending, completed, failed
    gateway_response_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    quotation = relationship("Quotation", back_populates="payments")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), unique=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), unique=True, nullable=False)
    booking_reference = Column(String(60), unique=True, index=True, nullable=False)
    # Status: confirmed, in_planning, vendor_assigned, logistics_ready, executing, completed, cancelled
    status = Column(String(40), default="confirmed")
    advance_paid = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)
    confirmed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    quotation = relationship("Quotation", back_populates="booking")
    event = relationship("Event", back_populates="booking")
    tasks = relationship("EventTask", back_populates="booking", cascade="all, delete-orphan")

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    business_name = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False)  # Catering, Decoration, Photography, AV/Sound, etc.
    locality = Column(String(100), default="RS Puram")
    phone = Column(String(25), nullable=False)
    email = Column(String(120), nullable=True)
    rating = Column(Float, default=4.8)
    is_verified = Column(Boolean, default=True)
    sample_pricing_desc = Column(String(200), nullable=True)

class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    venue_type = Column(String(80), default="marriage_hall")
    locality = Column(String(100), default="Peelamedu")
    capacity = Column(Integer, default=500)
    base_day_rate = Column(Float, default=50000.0)
    amenities_json = Column(Text, default="[]")
    is_verified = Column(Boolean, default=True)

class EventTask(Base):
    __tablename__ = "event_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(60), default="preparation")
    status = Column(String(30), default="pending")  # pending, in_progress, completed
    assigned_to = Column(String(100), default="Event Coordinator")
    due_date = Column(String(30), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    booking = relationship("Booking", back_populates="tasks")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, default=5)
    title = Column(String(150), nullable=True)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    event = relationship("Event", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    link = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")
