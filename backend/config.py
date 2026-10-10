import os

class Settings:
    PROJECT_NAME: str = "EVENTMATE AI – Smart Event Planning and Budget Management Platform"
    VERSION: str = "2.0.0"
    CITY: str = "Coimbatore"
    STATE: str = "Tamil Nadu"
    COUNTRY: str = "India"
    TIMEZONE: str = "Asia/Kolkata"
    CURRENCY_CODE: str = "INR"
    CURRENCY_SYMBOL: str = "₹"
    
    # Financial Rules
    DEFAULT_GST_RATE: float = 0.18  # 18% GST (9% CGST + 9% SGST)
    DEFAULT_ADVANCE_PERCENTAGE: float = 0.25  # 25% advance booking amount
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "eventmate-coimbatore-super-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eventmate.db")
    
    # Coimbatore Localities
    COIMBATORE_LOCALITIES = [
        "Gandhipuram",
        "RS Puram",
        "Peelamedu",
        "Saibaba Colony",
        "Singanallur",
        "Saravanampatti",
        "Avinashi Road",
        "Race Course",
        "Vadavalli",
        "Town Hall",
        "Ukkadam",
        "Ramanathapuram",
        "Hopes College",
        "Ganapathy",
        "Thudiyalur",
        "Kovaipudur",
        "Sundarapuram",
        "Kuniyamuthur",
        "Perur",
        "Kalapatti",
        "Neelambur",
        "Chinniampalayam",
        "Thondamuthur",
        "Pollachi Road",
        "Siruvani Road"
    ]
    
    # Coimbatore Venue Types
    COIMBATORE_VENUE_TYPES = [
        {"id": "marriage_hall", "name": "Marriage Hall / Kalyana Mandapam", "desc": "Traditional & modern marriage halls with dining hall"},
        {"id": "convention_centre", "name": "Convention Centre (e.g., CODISSIA style)", "desc": "Large capacity multi-purpose expo & convention spaces"},
        {"id": "hotel_banquet", "name": "Hotels & Banquet Halls", "desc": "AC banquet halls with in-house hospitality & audio setup"},
        {"id": "community_hall", "name": "Community & Samudaya Bhavans", "desc": "Cost-effective neighborhood community halls"},
        {"id": "college_campus", "name": "College / Educational Institution Campus", "desc": "Auditoriums, open air theatres, seminar halls, sports grounds"},
        {"id": "corporate_office", "name": "Corporate Office / Tech Park Facility", "desc": "Board rooms, training facilities, atrium spaces"},
        {"id": "conference_hall", "name": "Conference & Seminar Hall", "desc": "Acoustic treated hall with presentation & AV gear"},
        {"id": "restaurant_party_hall", "name": "Restaurant Party Hall", "desc": "Intimate dining space for compact celebrations"},
        {"id": "residential_property", "name": "Private Residence / Villa / Terrace", "desc": "Homely intimate ceremonies and private parties"},
        {"id": "outdoor_garden", "name": "Outdoor Lawn / Garden", "desc": "Lush open green spaces for evening & fairy-lit functions"},
        {"id": "farm_resort", "name": "Farm & Agro Resort Venue", "desc": "Scenic foothills towards Siruvani, Thondamuthur & Pollachi"},
        {"id": "temple_premises", "name": "Temple Premises (where permitted)", "desc": "Spiritual sanctum mandapams for traditional poojas"},
        {"id": "public_ground", "name": "Public Grounds / Stadium", "desc": "Large open grounds for marathons, sports & public gatherings"},
        {"id": "custom_venue", "name": "Other Customer-Specified Venue", "desc": "Any other customer-arranged location in Coimbatore"}
    ]

settings = Settings()
