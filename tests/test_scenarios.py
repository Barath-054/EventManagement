import pytest
import json
from decimal import Decimal
from fastapi.testclient import TestClient
from backend.main import app as _backend_app
from backend.database import SessionLocal, Base, engine
from backend.seed_data import seed_database
from backend.models import User, Event, Quotation, Payment, Booking, EventCategory, Service

client = TestClient(_backend_app)

def setup_module():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

def login_user(email: str, password: str):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"], res.json()["user"]

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert "Coimbatore" in res.json()["location"]

def test_workflow_1_wedding():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch categories & get Wedding
    cats = client.get("/api/categories").json()
    wedding_cat = next(c for c in cats if c["code"] == "wedding")
    
    # 2. Get wedding packages
    pkgs = client.get(f"/api/packages?category_id={wedding_cat['id']}").json()
    gold_pkg = next((p for p in pkgs if p["tier"] == "standard"), pkgs[0])
    
    # 3. Create event with dynamic requirements
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": wedding_cat["id"],
        "title": "Rajesh & Priya Grand Muhurtham Wedding",
        "event_date": "2026-11-20",
        "expected_attendees": 300,
        "budget": 200000.0,
        "venue_type": "marriage_hall",
        "preferred_locality": "Peelamedu",
        "package_id": gold_pkg["id"],
        "form_data": {
            "bride_name": "Priya",
            "groom_name": "Rajesh",
            "ceremony_type": "Kongu Vellalar Traditional Muhurtham",
            "muhurtham_timing": "06:00 - 07:30 AM",
            "catering_tradition": "Pure Kongu Vegetarian Banana Leaf"
        },
        "dietary_preferences": "pure_veg"
    })
    assert ev_res.status_code == 200
    event = ev_res.json()
    assert event["expected_attendees"] == 300
    assert event["form_data"]["bride_name"] == "Priya"

    # 4. Generate AI recommendations
    ai_res = client.post("/api/recommendations/analyze", json={
        "category_id": wedding_cat["id"],
        "attendees": 300,
        "budget": 200000.0,
        "venue_type": "marriage_hall",
        "preferred_locality": "Peelamedu",
        "indoor_outdoor": "indoor",
        "form_data": event["form_data"]
    })
    assert ai_res.status_code == 200
    recs = ai_res.json()
    assert len(recs["recommendations"]) > 0
    # Must have stage decor & banana leaf catering
    assert any("decor" in r["service_code"].lower() for r in recs["recommendations"])
    assert any("catering" in r["service_code"].lower() for r in recs["recommendations"])

    # 5. Generate Quotation
    quote_res = client.post("/api/quotations/generate", headers=headers, json={
        "event_id": event["id"]
    })
    assert quote_res.status_code == 200
    quote = quote_res.json()
    assert quote["grand_total"] > 0
    assert quote["advance_required"] > 0
    assert quote["status"] == "pending"

    # 6. Customer Approves Quotation
    appr_res = client.post(f"/api/quotations/{quote['id']}/approve", headers=headers)
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "approved"

    # 7. Make Advance Payment
    pay_res = client.post("/api/payments/process-advance", headers=headers, json={
        "quotation_id": quote["id"],
        "payment_type": "advance",
        "payment_method": "upi",
        "upi_id": "rajesh@oksbi"
    })
    assert pay_res.status_code == 200
    pay = pay_res.json()
    assert pay["status"] == "completed"

    # 8. Check Booking Confirmation & Milestone Tasks
    bk_res = client.get(f"/api/bookings/event/{event['id']}", headers=headers)
    assert bk_res.status_code == 200
    booking = bk_res.json()
    assert booking["status"] == "confirmed"
    assert len(booking["tasks"]) > 0

def test_workflow_2_birthday():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    cats = client.get("/api/categories").json()
    bday_cat = next(c for c in cats if c["code"] == "birthday")
    
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": bday_cat["id"],
        "title": "Aarav's 5th Superhero Birthday Fiesta",
        "event_date": "2026-10-25",
        "expected_attendees": 40,
        "budget": 45000.0,
        "venue_type": "restaurant_party_hall",
        "preferred_locality": "RS Puram",
        "form_data": {
            "age": "5 years",
            "party_theme": "Avengers Superhero",
            "cake_flavor": "Belgian Chocolate Fondant (3 Kg)",
            "games_needed": "Magic show & balloon twisting"
        }
    })
    assert ev_res.status_code == 200
    event = ev_res.json()
    assert event["expected_attendees"] == 40

    # AI recommendation check for birthday cake and entertainment
    ai_res = client.post("/api/recommendations/analyze", json={
        "category_id": bday_cat["id"],
        "attendees": 40,
        "budget": 45000.0,
        "venue_type": "restaurant_party_hall",
        "preferred_locality": "RS Puram",
        "form_data": event["form_data"]
    })
    assert ai_res.status_code == 200
    recs = ai_res.json()["recommendations"]
    assert any("balloon" in r["service_code"].lower() for r in recs)
    assert any("cake" in r["service_code"].lower() for r in recs)

def test_workflow_3_corporate_conference():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    cats = client.get("/api/categories").json()
    corp_cat = next(c for c in cats if c["code"] == "corporate")
    
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": corp_cat["id"],
        "title": "Kongu Tech Innovations Executive Summit",
        "event_date": "2026-12-05",
        "expected_attendees": 150,
        "budget": 120000.0,
        "venue_type": "conference_hall",
        "preferred_locality": "Avinashi Road",
        "form_data": {
            "company_name": "Kongu Tech Innovations Pvt Ltd",
            "event_objective": "Annual Tech Leadership & Product Showcase",
            "av_gear": "Dual 4K Laser Projectors + Collar mics",
            "registration_booths": 2
        }
    })
    assert ev_res.status_code == 200
    event = ev_res.json()

    ai_res = client.post("/api/recommendations/analyze", json={
        "category_id": corp_cat["id"],
        "attendees": 150,
        "budget": 120000.0,
        "venue_type": "conference_hall",
        "preferred_locality": "Avinashi Road",
        "form_data": event["form_data"]
    })
    recs = ai_res.json()["recommendations"]
    assert any("projector" in r["service_code"].lower() for r in recs)
    assert any("stage" in r["service_code"].lower() for r in recs)

def test_workflow_4_college_symposium():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    cats = client.get("/api/categories").json()
    college_cat = next(c for c in cats if c["code"] == "college")
    
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": college_cat["id"],
        "title": "PRAGYAN 2026 - National Technical Symposium",
        "event_date": "2026-10-30",
        "expected_attendees": 500,
        "budget": 90000.0,
        "venue_type": "college_campus",
        "preferred_locality": "Peelamedu",
        "form_data": {
            "institution": "Coimbatore Institute of Engineering",
            "department": "Computer Science & Artificial Intelligence",
            "participants": 500,
            "competition_count": 8,
            "awards_needed": "Championship mementos and certificates"
        }
    })
    assert ev_res.status_code == 200
    event = ev_res.json()

    ai_res = client.post("/api/recommendations/analyze", json={
        "category_id": college_cat["id"],
        "attendees": 500,
        "budget": 90000.0,
        "venue_type": "college_campus",
        "preferred_locality": "Peelamedu",
        "form_data": event["form_data"]
    })
    recs = ai_res.json()["recommendations"]
    assert any("sound" in r["service_code"].lower() or "pa" in r["service_code"].lower() for r in recs)
    assert any("refreshments" in r["service_code"].lower() or "catering" in r["service_code"].lower() for r in recs)

def test_workflow_5_cultural_event():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    cats = client.get("/api/categories").json()
    cult_cat = next(c for c in cats if c["code"] == "cultural")
    
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": cult_cat["id"],
        "title": "Kovai Isai Natya Kala Vizha 2026",
        "event_date": "2026-12-15",
        "expected_attendees": 250,
        "budget": 95000.0,
        "venue_type": "community_hall",
        "preferred_locality": "Saibaba Colony",
        "form_data": {
            "performances": "Bharatanatyam Recital + Carnatic Vocal Troupe",
            "artist_count": 12,
            "green_room_required": True,
            "lighting_profile": "Theatre profile spot + Warm par washes"
        }
    })
    assert ev_res.status_code == 200

def test_workflow_6_sports_tournament():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    cats = client.get("/api/categories").json()
    sports_cat = next(c for c in cats if c["code"] == "sports")
    
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": sports_cat["id"],
        "title": "Coimbatore Corporate Cricket Championship T10",
        "event_date": "2026-11-14",
        "expected_attendees": 120,
        "budget": 60000.0,
        "venue_type": "public_ground",
        "preferred_locality": "Gandhipuram",
        "form_data": {
            "sport_type": "Cricket T10",
            "teams": 16,
            "players": 120,
            "first_aid": "Paramedic staff on field required",
            "electrolyte_stations": "Unlimited hydration counters"
        }
    })
    assert ev_res.status_code == 200
    event = ev_res.json()

    ai_res = client.post("/api/recommendations/analyze", json={
        "category_id": sports_cat["id"],
        "attendees": 120,
        "budget": 60000.0,
        "venue_type": "public_ground",
        "preferred_locality": "Gandhipuram",
        "form_data": event["form_data"]
    })
    recs = ai_res.json()["recommendations"]
    assert any("medic" in r["service_code"].lower() or "first_aid" in r["service_code"].lower() for r in recs)
    assert any("hydration" in r["service_code"].lower() for r in recs)

def test_workflow_7_custom_event():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    cats = client.get("/api/categories").json()
    custom_cat = next(c for c in cats if c["code"] == "custom")
    
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": custom_cat["id"],
        "title": "Western Ghats Agri-Eco Community Summit",
        "event_date": "2026-12-22",
        "expected_attendees": 80,
        "budget": 70000.0,
        "venue_type": "farm_resort",
        "preferred_locality": "Siruvani Road",
        "is_custom": True,
        "form_data": {
            "custom_purpose": "Agro-forestry knowledge sharing & local farmer dinner",
            "special_needs": "Outdoor fire pit & organic farm lunch"
        }
    })
    assert ev_res.status_code == 200
    event = ev_res.json()
    assert event["is_custom"] == True

def test_price_update_and_revisions():
    token, user = login_user("client@eventmate.ai", "Client@123")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create event
    cats = client.get("/api/categories").json()
    cat = cats[0]
    svcs = client.get("/api/services").json()
    svc1, svc2 = svcs[0], svcs[1]
    
    ev_res = client.post("/api/events", headers=headers, json={
        "category_id": cat["id"],
        "title": "Quotation Price Test Function",
        "event_date": "2026-12-01",
        "expected_attendees": 50,
        "budget": 50000.0,
        "services": [
            {"service_id": svc1["id"], "quantity": 1.0},
            {"service_id": svc2["id"], "quantity": 50.0}
        ]
    })
    event = ev_res.json()
    
    # 1. Preview price calculation
    prev = client.post("/api/quotations/preview", json={
        "attendees": 50,
        "services": [
            {"service_id": svc1["id"], "quantity": 1.0},
            {"service_id": svc2["id"], "quantity": 50.0}
        ]
    }).json()
    initial_total = prev["grand_total"]
    assert initial_total > 0
    
    # 2. Generate initial formal quotation
    quote = client.post("/api/quotations/generate", headers=headers, json={
        "event_id": event["id"]
    }).json()
    assert quote["grand_total"] == initial_total
    assert quote["version"] == 1
    
    # 3. Request revision with modified quantity (e.g. 100 instead of 50)
    rev_res = client.post(f"/api/quotations/{quote['id']}/request-change", headers=headers, json={
        "reason": "Increasing attendee food count from 50 to 100",
        "modified_services": [
            {"service_id": svc1["id"], "quantity": 1.0},
            {"service_id": svc2["id"], "quantity": 100.0}
        ]
    })
    assert rev_res.status_code == 200
    revised_quote = rev_res.json()
    assert revised_quote["version"] == 2
    assert revised_quote["grand_total"] > initial_total

def test_customer_isolation_security():
    import uuid
    rand_suffix = uuid.uuid4().hex[:6]
    # Register customer 2
    reg_res = client.post("/api/auth/register", json={
        "full_name": "Suresh Kumar",
        "email": f"suresh_{rand_suffix}@kovai.com",
        "phone": "+91 99440 12345",
        "password": "Password@123",
        "role": "customer"
    })
    assert reg_res.status_code == 200
    token2 = reg_res.json()["access_token"]
    user2 = reg_res.json()["user"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Create event as customer 2
    cats = client.get("/api/categories").json()
    ev2 = client.post("/api/events", headers=headers2, json={
        "category_id": cats[0]["id"],
        "title": "Suresh Private Function",
        "event_date": "2026-11-28",
        "expected_attendees": 75,
        "budget": 40000.0
    }).json()
    
    # Customer 1 tries to access Suresh's event
    token1, user1 = login_user("client@eventmate.ai", "Client@123")
    headers1 = {"Authorization": f"Bearer {token1}"}
    forbidden_res = client.get(f"/api/events/{ev2['id']}", headers=headers1)
    assert forbidden_res.status_code == 403, "Customer 1 should be forbidden from accessing Customer 2's event"

def test_admin_can_add_category_and_service():
    import uuid
    cat_code = f"drone_racing_{uuid.uuid4().hex[:6]}"
    svc_code = f"fpv_mesh_{uuid.uuid4().hex[:6]}"
    
    admin_token, admin = login_user("admin@eventmate.ai", "Admin@123")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin creates new category
    new_cat_res = client.post("/api/categories", headers=headers, json={
        "code": cat_code,
        "name": "Drone Racing & Aero Expos",
        "name_tamil": "ட்ரோன் பந்தயம் & வான்வெளி கண்காட்சி",
        "description": "High-octane drone racing events across Coimbatore grounds.",
        "icon": "lightning-bolt",
        "display_order": 12,
        "event_types": ["FPV Drone Obstacle Race", "Autonomous Drone Fly-off"]
    })
    assert new_cat_res.status_code == 200
    created_cat = new_cat_res.json()
    assert created_cat["code"] == cat_code
    
    # Admin creates new service
    svc_res = client.post("/api/services", headers=headers, json={
        "service_category_id": 1,
        "code": svc_code,
        "name": "High-Density Drone Safety Mesh Enclosure",
        "description": "Industrial grade containment nets protecting spectators",
        "unit_type": "per_day",
        "base_price": 18500.0,
        "min_quantity": 1,
        "eligible_categories": [cat_code]
    })
    assert svc_res.status_code == 200
    assert svc_res.json()["base_price"] == 18500.0

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_scenarios.py"])
