# EVENTMATE AI – Smart Event Planning and Budget Management Platform

> **Location:** Tailored specifically for **Coimbatore, Tamil Nadu, India**  
> **Platform Version:** 2.0.0  
> **Architecture:** FastAPI (Python 3.13) + SQLAlchemy Relational Models + SQLite + Universal Decimal Pricing Engine + Rule-Based AI Recommendation Studio + Vanilla CSS Glassmorphism & Responsive Web Frontend

---

## 1. What Was Changed & Architectural Evolution

The platform has been expanded from a marriage-only planning concept into a unified, enterprise-grade multi-category event planning and management platform:

1. **Generalized Relational Data Models**:
   - Replaced marriage-exclusive entities with reusable models: `EventCategory`, `EventType`, `Event`, `EventRequirement` (dynamic JSON-backed schemas), `EventPackage`, `ServiceCategory`, `Service`, `PackageService`, `EventService`, `AIRecommendation`, `Quotation`, `QuotationItem`, `QuotationRevision`, `Payment`, `Booking`, `Vendor`, `Venue`, `EventTask`, `Review`, and `AuditLog`.
   - Marriage planning remains a 1st-class citizen (Kongu Vellalar Muhurtham, Iyer/Iyengar rituals, reception feasts, Nadaswaram, etc.), but shares the exact same core pipeline as corporate summits, sports tournaments, and college symposiums.

2. **Universal Decimal Pricing Engine (`backend/pricing_engine.py`)**:
   - Implemented exact Decimal arithmetic to eliminate floating-point calculation discrepancies.
   - Supports 7 distinct pricing units: `per_person`, `per_hour`, `per_day`, `per_item`, `per_seat`, `per_event`, and `per_worker`.
   - Incorporates Coimbatore financial localization: **18% GST (9% CGST + 9% SGST)** and **25% advance booking amount**.
   - Generates immutable snapshot records for quotations to prevent historical bills from fluctuating when catalog prices change.

3. **Multi-Category AI Recommendation Engine (`backend/recommendation_ai.py`)**:
   - Rule-based AI analyzer evaluating Event Category, Expected Guests, Budget, Venue Type, Coimbatore Locality, and Indoors/Outdoors constraints.
   - Generates prioritized arrangements with **transparent rationale ("Why recommended?")**, budget feasibility scores (0-100%), cost-saving tips, and localized Coimbatore venue advice.

4. **Dynamic 4-Step Requirements Wizard (`frontend/js/app.js`)**:
   - Replaced static wedding forms with a responsive wizard where Step 2 renders category-specific input questions and Step 3 delivers customized packages and AI advice.

5. **Security & Customer Isolation**:
   - Role-Based Access Control (`customer`, `admin`, `vendor`).
   - Strict data isolation ensuring customers cannot view or modify other customers' event records.

6. **Bilingual Localization**:
   - Full English and Tamil toggle switch (`EN` / `தமிழ்`) supporting Coimbatore event terminology.

---

## 2. Supported Event Categories (Coimbatore, Tamil Nadu)

| Category Code | Category Name | Key Sub-Types Supported |
| :--- | :--- | :--- |
| `wedding` | **Category A: Weddings & Family Ceremonies** | Traditional Muhurtham, Engagement, Reception, Sangeet/Mehendi, Anniversary, Seemantham/Baby Shower, Naming Ceremony, 1st Birthday, Ear-piercing (Kaadhu Kuthu), Grihapravesham, Puberty Ceremony (Manjal Neerattu Vizha), Sashtiabdapoorthi, Family Reunion |
| `birthday` | **Category B: Birthday & Personal Celebrations** | Children's Themed Birthday, Adult Birthday Bash, Surprise Party, Milestone (18th, 25th, 50th), Graduation, Farewell, Private Family Dinner |
| `corporate` | **Category C: Corporate & Business Events** | Annual Day, Executive Conference & Summit, Seminars & Workshops, Product Launches, Business Networking, Dealer Meets, Investor Presentations |
| `college` | **Category D: College & Educational Events** | National Technical Symposiums, Inter-Collegiate Cultural Fests, College Annual Day, Freshers' Day, Farewell Day, Convocation & Graduation, Hackathons, Project Expos, Alumni Reunions |
| `cultural` | **Category E: Cultural & Community Events** | Tamil Cultural Celebrations, Carnatic Music Concerts (Isai Vizha), Bharatanatyam Arangetrams, Folk Art & Karagattam Programs, Community Gatherings, Charity Fundraisers |
| `religious` | **Category F: Religious & Traditional Celebrations** | Temple Festivals (Thiruvizha), Maha Ganapathi & Sudarshana Homams, Satyanarayana Swamy Pooja, Community Bhajans, Annadhanam, Family Rituals |
| `festival` | **Category G: Festival & Seasonal Celebrations** | Samathuva Pongal, Tamil New Year (Chithirai), Diwali Gala, Christmas & Year-End Fellowship, New Year Welcome, Onam Sadya, Gated Community Fests |
| `entertainment` | **Category H: Entertainment & Social Events** | Live Music Concerts, DJ Parties, Stand-Up Comedy Specials, Fashion Shows, Talent Showcases, Food & Music Carnivals |
| `sports` | **Category I: Sports & Outdoor Events** | Cricket Premier Tournaments (T10/T20), Corporate Football/Futsal Leagues, Badminton Open, Coimbatore Marathon, Fitness Competitions, Sports Days |
| `exhibition` | **Category J: Exhibitions & Special Events** | Trade Exhibitions, Handloom & Textile Fairs, Food & Agri Expos, Job Melas, Startup Summits, Art & Craft Showcases |
| `custom` | **Category K: Custom Events** | Bespoke user-defined events with customizable purpose, venue, and unique arrangements |

---

## 3. Coimbatore-Specific Customizations

- **Supported Localities**: Gandhipuram, RS Puram, Peelamedu, Saibaba Colony, Singanallur, Saravanampatti, Avinashi Road, Race Course, Vadavalli, Town Hall, Ukkadam, Ramanathapuram, Hopes College, Ganapathy, Thudiyalur, Kovaipudur, Perur, Kalapatti, Neelambur, Thondamuthur, Pollachi Road, Siruvani Road.
- **Configurable Venue Types**: Kalyana Mandapams / Marriage Halls, Convention Centres (e.g. CODISSIA style), Hotels & Banquet Halls, Community & Samudaya Bhavans, College Campuses (Auditoriums/OAT), Corporate Tech Parks, Conference Halls, Farm & Agro Resorts (Siruvani/Pollachi Road), Temple Premises, Public Grounds/Stadiums.
- **Financial Standards**: Indian Rupee (INR - `₹`), Asia/Kolkata (IST), Indian date formats, 18% GST (9% CGST + 9% SGST).

---

## 4. How to Create a New Event Category

### Method A: Via the Admin UI Console
1. Log in as Admin (`admin@eventmate.ai` / `Admin@123`).
2. Click **Admin Console** in the top navbar.
3. Click the **+ Add Category** button.
4. Enter the English Name, Tamil Name, unique slug code (e.g., `drone_expo`), and description.
5. Click **Create Category**. The category is immediately active and appears in the categories grid.

### Method B: Via the Admin REST API
Send an authenticated HTTP POST request:
```bash
POST /api/categories
Authorization: Bearer <ADMIN_JWT_TOKEN>
Content-Type: application/json

{
  "name": "Robotics & AI Expo",
  "name_tamil": "ரோபோடிக்ஸ் & ஏஐ கண்காட்சி",
  "code": "robotics_expo",
  "description": "State-level robotics competitions and automation showcases",
  "icon": "chip",
  "display_order": 12,
  "event_types": ["Autonomous Robot Race", "Combat Robotics"]
}
```

---

## 5. How to Configure Service Prices and Units

### Service Pricing Methods
Each service in `backend/models.py` has a configurable `unit_type`:
- `per_person`: Calculated as `attendees * unit_price` (e.g., Catering)
- `per_hour`: Calculated as `hours * unit_price` (e.g., Equipment rental)
- `per_day`: Calculated as `days * unit_price` (e.g., Line-Array Sound PA, Stage lighting)
- `per_item`: Calculated as `items * unit_price` (e.g., Custom Birthday Cake per kg, LED Wall panels)
- `per_seat`: Calculated as `seats * unit_price` (e.g., Cushion banquet chairs)
- `per_event`: Flat service fee (e.g., Royal Wedding Stage Decoration, MC Host)
- `per_worker`: Calculated as `workers * unit_price` (e.g., On-site event coordinators)

### Updating Service Prices Via REST API
```bash
PUT /api/services/{service_id}
Authorization: Bearer <ADMIN_JWT_TOKEN>
Content-Type: application/json

{
  "service_category_id": 1,
  "code": "wedding_stage_decor",
  "name": "Grand Royal Wedding Stage Backdrop & Florals",
  "description": "Customized floral backdrop with natural jasmine, roses and LED profiles",
  "unit_type": "per_event",
  "base_price": 50000.0,
  "min_quantity": 1,
  "eligible_categories": ["wedding"],
  "is_mandatory": true
}
```

---

## 6. How to Run the Application

### 1. Requirements
- Python 3.10+ (tested on Python 3.13)
- Dependencies installed: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `python-multipart`, `python-jose`

### 2. Startup Command
Run the application from the project root:
```powershell
python run.py
```

### 3. Access URLs
- **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc API Docs:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 4. Default Seeded Credentials
- **Client Account:**  
  Email: `client@eventmate.ai` | Password: `Client@123`
- **Administrator Account:**  
  Email: `admin@eventmate.ai` | Password: `Admin@123`

---

## 7. How to Test the Complete Workflows

### Automated Test Suite (11 Tests)
Run pytest in terminal:
```powershell
python -m pytest tests/test_scenarios.py -v
```
This tests:
1. `test_workflow_1_wedding`: Traditional Muhurtham with 300 guests, banana leaf catering, gold package, quotation approval, advance payment, and task creation.
2. `test_workflow_2_birthday`: 4th/5th birthday fiesta with 40 guests, custom fondant cake, balloon decor, and magic show.
3. `test_workflow_3_corporate_conference`: Tech summit with 150 guests on Avinashi Road, dual 4K laser projectors, badging, and executive lunch.
4. `test_workflow_4_college_symposium`: National technical symposium with 500 participants, auditorium PA, packed meals, and trophies.
5. `test_workflow_5_cultural_event`: Classical dance & Isai Vizha with green room management and theatre profile lights.
6. `test_workflow_6_sports_tournament`: 16-team cricket tournament with paramedic station, hydration counter, and championship medals.
7. `test_workflow_7_custom_event`: Custom Western Ghats agro-community event with manually entered inputs.
8. `test_price_update_and_revisions`: Live recalculation upon changing quantities and creation of versioned quotation revisions.
9. `test_customer_isolation_security`: Verifies Customer A cannot access Customer B's records (HTTP 403 Forbidden).
10. `test_admin_can_add_category_and_service`: Verifies dynamic addition of categories and services without app restart.
11. `test_health_check`: Verifies server connectivity and Coimbatore location tagging.

### Interactive UI One-Click Testers
On the landing page, 7 quick-action buttons are available directly beneath the hero:
- **💍 1. Wedding (300 guests)**
- **🎂 2. Birthday (40 guests)**
- **💼 3. Corporate (150 guests)**
- **🎓 4. College Fest (500 guests)**
- **🎭 5. Cultural Dance**
- **🏆 6. Sports League**
- **🎨 7. Custom Event**

Clicking any button automatically opens the Dynamic Wizard pre-configured for that exact test scenario!

---

## 8. External Integrations Requiring Production Credentials

The application includes working mock/simulation drivers for testing. For production deployment in Coimbatore, connect the following external service credentials:

1. **Payment Gateway (Razorpay / Cashfree / PhonePe Payment Gateway)**:
   - Provide `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in environment variables to replace the local mock UPI/Card simulator in `backend/routers/payments_router.py`.
2. **SMS / WhatsApp Notification Gateway (Gupshup / MSG91 / Twilio)**:
   - Configure credentials in `backend/config.py` to dispatch real SMS / WhatsApp booking confirmations to Coimbatore clients and vendors.
3. **Map & Locality Geocoding Service (Google Maps API / Mapbox)**:
   - Add `GOOGLE_MAPS_API_KEY` for interactive venue driving distance and routing across Coimbatore localities (e.g. from Gandhipuram to Siruvani).
4. **Production LLM Provider (Google Gemini API / OpenAI)**:
   - The current engine uses deterministic, explainable rule-based heuristics (`backend/recommendation_ai.py`). Provide `GEMINI_API_KEY` to enable free-form conversational event design extensions.
