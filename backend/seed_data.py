import json
from sqlalchemy.orm import Session
from backend.auth import get_password_hash
from backend.models import (
    User, CustomerProfile, EventCategory, EventType,
    ServiceCategory, Service, EventPackage, PackageService,
    Vendor, Venue
)

def seed_database(db: Session):
    # Check if already seeded
    if db.query(EventCategory).count() > 0:
        return

    # 1. Seed Users (Admin, Customer, Vendor)
    admin_user = User(
        full_name="Karthik R (System Admin)",
        email="admin@eventmate.ai",
        phone="+91 98422 10001",
        password_hash=get_password_hash("Admin@123"),
        role="admin",
        is_active=True
    )
    db.add(admin_user)
    
    client_user = User(
        full_name="Ananya Sundaram",
        email="client@eventmate.ai",
        phone="+91 97890 23456",
        password_hash=get_password_hash("Client@123"),
        role="customer",
        is_active=True
    )
    db.add(client_user)
    db.flush()

    # Client Profile
    client_profile = CustomerProfile(
        user_id=client_user.id,
        organization_name="Sundaram Ventures",
        address="142, East Sambandam Road, RS Puram, Coimbatore - 641002",
        preferred_locality="RS Puram",
        gst_number="33AABCS1429E1Z2"
    )
    db.add(client_profile)

    # 2. Seed Event Categories & Sub-types (Categories A through K)
    categories_data = [
        {
            "code": "wedding",
            "name": "Weddings & Family Ceremonies",
            "name_tamil": "திருமணம் மற்றும் குடும்ப விழாக்கள்",
            "description": "Muhurtham weddings, engagements, grand receptions, seemantham, naming ceremonies, grihapravesham & family gatherings in Coimbatore.",
            "icon": "heart",
            "order": 1,
            "subtypes": [
                ("Wedding / Traditional Muhurtham", "திருமணம் / முகூர்த்தம்"),
                ("Engagement Ceremony", "நிச்சயதார்த்தம்"),
                ("Wedding Reception", "வரவேற்பு நிகழ்ச்சி"),
                ("Pre-wedding Sangeet & Mehendi", "மெஹந்தி மற்றும் சங்கீத்"),
                ("Post-wedding Celebrations", "மறுவீடு விருந்து"),
                ("Wedding Anniversary", "திருமண நாள் விழா"),
                ("Baby Shower / Seemantham", "வளைகாப்பு / சீமந்தம்"),
                ("Naming Ceremony / Thottil", "பெயர் சூட்டு விழா / தொட்டில்"),
                ("First Birthday Celebration", "முதல் பிறந்தநாள் விழா"),
                ("Ear-piercing / Kaadhu Kuthu", "காது குத்து விழா"),
                ("Housewarming / Grihapravesham", "புதுமனை புகுவிழா"),
                ("Puberty Ceremony / Manjal Neerattu", "மஞ்சள் நீராட்டு விழா"),
                ("Retirement Celebration / Sashtiabdapoorthi", "பணிநிறைவு / சஷ்டியப்தபூர்த்தி"),
                ("Family Reunion", "குடும்ப சந்திப்பு விழா")
            ]
        },
        {
            "code": "birthday",
            "name": "Birthday & Personal Celebrations",
            "name_tamil": "பிறந்தநாள் மற்றும் தனிநபர் கொண்டாட்டங்கள்",
            "description": "Fun-filled milestone birthdays, surprise bashes, children's theme parties, and private family dinners.",
            "icon": "cake",
            "order": 2,
            "subtypes": [
                ("Children's Themed Birthday", "குழந்தைகள் தீம் பிறந்தநாள்"),
                ("Adult Birthday Bash", "வயதுவந்தோர் பிறந்தநாள் விழா"),
                ("Surprise Birthday Party", "திடீர் ஆச்சரிய பிறந்தநாள்"),
                ("Milestone Birthday (18th, 25th, 50th)", "மைல்கல் பிறந்தநாள் விழா"),
                ("Graduation Celebration", "பட்டமளிப்பு கொண்டாட்டம்"),
                ("Farewell Party", "பிரியாவிடை விழா"),
                ("Welcome Party", "வரவேற்பு விருந்து"),
                ("Private Family Celebration", "தனிப்பட்ட குடும்ப கொண்டாட்டம்")
            ]
        },
        {
            "code": "corporate",
            "name": "Corporate & Business Events",
            "name_tamil": "கார்ப்பரேட் மற்றும் வணிக நிகழ்வுகள்",
            "description": "High-impact conferences, annual general meetings, product launches, dealer meets, and team offsites.",
            "icon": "briefcase",
            "order": 3,
            "subtypes": [
                ("Corporate Annual Day", "கார்ப்பரேட் ஆண்டு விழா"),
                ("Business Conference & Summit", "வணிக மாநாடு"),
                ("Seminars & Executive Workshops", "கருத்தரங்கு மற்றும் பயிலரங்கம்"),
                ("Product Launch Event", "புதிய தயாரிப்பு வெளியீட்டு விழா"),
                ("Business Networking Meet", "வணிக தொடர்புகள் சந்திப்பு"),
                ("Company Anniversary Celebration", "நிறுவன ஆண்டு நிறைவு விழா"),
                ("Employee Appreciation & Awards", "பணியாளர் பாராட்டு விழா"),
                ("Team-Building Offsite", "குழு கட்டமைப்பு முகாம்"),
                ("Dealer & Vendor Meet", "வியாபாரிகள் சந்திப்பு"),
                ("Investor & Board Presentation", "முதலீட்டாளர் விளக்கக்காட்சி")
            ]
        },
        {
            "code": "college",
            "name": "College & Educational Events",
            "name_tamil": "கல்லூரி மற்றும் கல்வி நிறுவன நிகழ்வுகள்",
            "description": "National symposiums, cultural fests, hackathons, sports days, graduation ceremonies across Coimbatore campuses.",
            "icon": "academic-cap",
            "order": 4,
            "subtypes": [
                ("National Technical Symposium", "தேசிய தொழில்நுட்ப கருத்தரங்கு"),
                ("Inter-Collegiate Cultural Festival", "கல்லூரிகளுக்கிடையேயான கலை விழா"),
                ("College Annual Day Celebrations", "கல்லூரி ஆண்டு விழா"),
                ("Freshers' Welcome Day", "புதிய மாணவர் வரவேற்பு நாள்"),
                ("College Farewell Day", "கல்லூரி பிரியாவிடை நாள்"),
                ("Graduation & Convocation Ceremony", "பட்டமளிப்பு விழா"),
                ("Department Symposium & Hackathon", "துறை கருத்தரங்கு & ஹேக்கத்தான்"),
                ("Project Exhibition & Tech Expo", "திட்ட கண்காட்சி"),
                ("Distinguished Guest Lectures", "சிறப்பு விருந்தினர் உரை"),
                ("Alumni Reunion Meet", "முன்னாள் மாணவர் சந்திப்பு"),
                ("School Annual Day & Sports Meet", "பள்ளி ஆண்டு விழா மற்றும் விளையாட்டு")
            ]
        },
        {
            "code": "cultural",
            "name": "Cultural & Community Events",
            "name_tamil": "கலாச்சார மற்றும் சமுதாய விழாக்கள்",
            "description": "Tamil arts, Carnatic concerts, Bharatanatyam Arangetrams, folk-art festivals, and public gatherings.",
            "icon": "sparkles",
            "order": 5,
            "subtypes": [
                ("Tamil Cultural Celebrations", "தமிழ் பாரம்பரிய கலை விழா"),
                ("Carnatic Music Concert / Isai Vizha", "கர்நாடக இசை கச்சேரி"),
                ("Bharatanatyam Arangetram / Dance", "பரதநாட்டிய அரங்கேற்றம்"),
                ("Folk Art & Karagattam Programs", "நாட்டுப்புற கலை மற்றும் கரகாட்டம்"),
                ("Community Social Gathering", "சமூக ஒன்றுகூடல்"),
                ("Cultural Talent Competitions", "கலாச்சார திறமைப் போட்டிகள்"),
                ("Charity Fundraiser Evening", "நிதி திரட்டும் அறக்கட்டளை நிகழ்வு"),
                ("Public Awareness & Civic Programs", "பொது விழிப்புணர்வு நிகழ்ச்சி")
            ]
        },
        {
            "code": "religious",
            "name": "Religious & Traditional Celebrations",
            "name_tamil": "ஆன்மீக மற்றும் பாரம்பரிய வழிபாடுகள்",
            "description": "Temple festivals, Homams, community prayer meets, Sathyanarayana poojas with customized tradition compliance.",
            "icon": "shield-check",
            "order": 6,
            "subtypes": [
                ("Maha Ganapathi & Sudarshana Homam", "மகா கணபதி மற்றும் சுதர்சன ஹோமம்"),
                ("Temple Thiruvizha & Annadhanam", "கோவில் திருவிழா மற்றும் அன்னதானம்"),
                ("Satyanarayana Swamy Pooja", "சத்யநாராயண பூஜை"),
                ("Community Bhajan & Prayer Meeting", "சமூக பஜனை மற்றும் கூட்டுப் பிரார்த்தனை"),
                ("Spiritual Discourse & Upanyasam", "ஆன்மீக உபன்யாசம்"),
                ("Traditional Family Rituals", "குடும்ப பாரம்பரிய சடங்குகள்")
            ]
        },
        {
            "code": "festival",
            "name": "Festival & Seasonal Celebrations",
            "name_tamil": "பண்டிகைகள் மற்றும் பருவகால கொண்டாட்டங்கள்",
            "description": "Pongal Vizha, Tamil New Year, Diwali, Christmas gala, Onam Sadya, and New Year community galas.",
            "icon": "sun",
            "order": 7,
            "subtypes": [
                ("Samathuva Pongal Celebration", "சமத்துவ பொங்கல் திருவிழா"),
                ("Tamil New Year Celebration / Chithirai", "தமிழ்ப் புத்தாண்டு கொண்டாட்டம்"),
                ("Diwali Celebration Gala", "தீபாவளி சிறப்பு விழா"),
                ("Christmas & Year-End Fellowship", "கிறிஸ்துமஸ் பெருவிழா"),
                ("New Year Welcome Eve", "புத்தாண்டு கொண்டாட்டம்"),
                ("Onam Traditional Celebration & Sadya", "ஓணம் பாரம்பரிய கொண்டாட்டம்"),
                ("Residential Gated Community Festival", "குடியிருப்பு வளாக திருவிழா")
            ]
        },
        {
            "code": "entertainment",
            "name": "Entertainment & Social Events",
            "name_tamil": "பொழுதுபோக்கு மற்றும் சமூக நிகழ்ச்சிகள்",
            "description": "Live musical concerts, DJ sound blasts, stand-up comedy specials, talent shows, and private dance parties.",
            "icon": "music",
            "order": 8,
            "subtypes": [
                ("Live Music Band Concert", "இசைக்குழு நேரடி கச்சேரி"),
                ("DJ Night & Dance Party", "டிஜே இசை & நடன இரவு"),
                ("Stand-Up Comedy Show", "நகைச்சுவை நிகழ்ச்சி"),
                ("Fashion Show & Pageant", "ஆடை வடிவமைப்பு அணிவகுப்பு"),
                ("Talent Showcase & Reality Audition", "திறமை தேடல் நிகழ்ச்சி"),
                ("Food & Music Carnival", "உணவு மற்றும் இசை திருவிழா")
            ]
        },
        {
            "code": "sports",
            "name": "Sports & Outdoor Tournaments",
            "name_tamil": "விளையாட்டு மற்றும் வெளிப்புற போட்டிகள்",
            "description": "Cricket leagues, corporate football, badminton tournaments, marathons, and collegiate athletics.",
            "icon": "trophy",
            "order": 9,
            "subtypes": [
                ("Cricket Premier Tournament (T10/T20)", "கிரிக்கெட் பிரீமியர் தொடர்"),
                ("Corporate Football / Futsal League", "கால்பந்து லீக் போட்டி"),
                ("Badminton Open Championship", "இறகுப்பந்து சாம்பியன்ஷிப்"),
                ("Coimbatore City Marathon / Walkathon", "கோவை மாரத்தான் ஓட்டம்"),
                ("Fitness Competition / CrossFit", "உடற்தகுதி போட்டி"),
                ("Outdoor Team-Building Sports Day", "வெளிப்புற விளையாட்டு விழா"),
                ("Inter-School Athletic Championship", "பள்ளி தடகளப் போட்டிகள்")
            ]
        },
        {
            "code": "exhibition",
            "name": "Exhibitions & Special Trade Expos",
            "name_tamil": "கண்காட்சிகள் மற்றும் சிறப்பு வர்த்தக மேளாக்கள்",
            "description": "Industrial trade fairs, art & craft expos, property shows, food fairs, job expos, and startup summits.",
            "icon": "store",
            "order": 10,
            "subtypes": [
                ("Industrial & Machinery Trade Expo", "தொழில்துறை வர்த்தக கண்காட்சி"),
                ("Handloom & Textile Fair", "கைத்தறி மற்றும் ஜவுளி மேளா"),
                ("Food & Organic Agri Exhibition", "உணவு & இயற்கை விவசாய கண்காட்சி"),
                ("Career Fair & Mega Job Mela", "வேலைவாய்ப்பு முகாம்"),
                ("Startup Summit & Investor Pavilion", "ஸ்டார்ட்அப் உச்சி மாநாடு"),
                ("Art & Craft Showcase", "கைவினைப் பொருட்கள் கண்காட்சி")
            ]
        },
        {
            "code": "custom",
            "name": "Custom Tailored Event",
            "name_tamil": "விருப்பத்திற்கேற்ப தனிப்பயனாக்கப்பட்ட நிகழ்வு",
            "description": "Design an entirely bespoke event with specific arrangements, unique venues, and personalized rules.",
            "icon": "color-swatch",
            "order": 11,
            "subtypes": [
                ("Bespoke Private Event", "தனிப்பயன் தனியார் நிகழ்வு"),
                ("Unique Theme Celebration", "தனித்துவ தீம் கொண்டாட்டம்"),
                ("Hybrid Multi-Purpose Event", "பலநோக்கு கலப்பு நிகழ்வு")
            ]
        }
    ]

    category_models = {}
    for cat_data in categories_data:
        cat = EventCategory(
            code=cat_data["code"],
            name=cat_data["name"],
            name_tamil=cat_data["name_tamil"],
            description=cat_data["description"],
            icon=cat_data["icon"],
            display_order=cat_data["order"],
            is_active=True
        )
        db.add(cat)
        db.flush()
        category_models[cat.code] = cat

        for st_name, st_tamil in cat_data["subtypes"]:
            subtype = EventType(
                category_id=cat.id,
                name=st_name,
                name_tamil=st_tamil,
                description=f"Specialized setup for {st_name}",
                is_active=True
            )
            db.add(subtype)

    # 3. Seed Service Categories
    service_cats_data = [
        ("stage", "Stage & Backdrop", "template", 1),
        ("decoration", "Decorations & Floral Design", "sparkles", 2),
        ("catering", "Catering & Refreshments", "cake", 3),
        ("lighting", "Lighting & Special Effects", "light-bulb", 4),
        ("sound", "Sound & Audio Visual", "volume-up", 5),
        ("screens", "LED Screens & Projectors", "desktop-computer", 6),
        ("photography", "Photography & Cinematography", "camera", 7),
        ("entertainment", "Entertainment & Emcee", "music", 8),
        ("seating", "Seating & Banquet Furniture", "chair", 9),
        ("registration", "Registration & Guest Management", "identification", 10),
        ("sports_gear", "Sports Infrastructure & Equipment", "trophy", 11),
        ("manpower", "Logistics, Security & Coordination", "users", 12),
        ("awards", "Mementos, Trophies & Printing", "badge-check", 13)
    ]
    
    svc_cat_models = {}
    for code, name, icon, order in service_cats_data:
        sc = ServiceCategory(code=code, name=name, icon=icon, display_order=order)
        db.add(sc)
        db.flush()
        svc_cat_models[code] = sc

    # 4. Seed Reusable Service Catalog
    services_data = [
        # Decoration
        ("wedding_stage_decor", "stage", "Grand Royal Wedding Stage Backdrop & Florals", "Customized traditional/contemporary wedding stage with natural jasmine, roses, marigold, LED backdrops", "per_event", 45000.0, 1, ["wedding"], True),
        ("birthday_theme_balloon_decor", "decoration", "Themed Balloon Arch & Birthday Backdrop", "Organic balloon styling, neon sign, customized cutouts, and cake table setup", "per_event", 12000.0, 1, ["birthday"], True),
        ("corporate_conference_stage", "stage", "Corporate Stage with Executive Lectern & Backdrop", "Matte finished branded stage, high-density lectern with mic mounts, and sponsor banner framing", "per_event", 25000.0, 1, ["corporate", "college"], True),
        ("cultural_dance_stage_setup", "stage", "Classical Dance Stage with Nataraja Mandapam", "Resilient wooden staging with brass lamps, floral side hangings, and quick-change backstage partitions", "per_event", 28000.0, 1, ["cultural"], True),
        
        # Catering
        ("traditional_banana_leaf_catering", "catering", "Traditional Kongu / Tamil Banana Leaf Feast", "Authentic 24-item pure vegetarian muhurtham meal served on plantain leaves with payasam, vadai, sambar", "per_person", 350.0, 50, ["wedding", "cultural", "religious", "festival"], True),
        ("party_buffet_catering", "catering", "Continental & Indian Party Buffet", "Live pasta/chaat counter, starter platters, main course curry selection, rice, desserts, and welcome drink", "per_person", 450.0, 25, ["birthday", "entertainment", "custom"], True),
        ("corporate_high_tea_lunch", "catering", "Executive High-Tea & Multi-Cuisine Lunch", "Two morning/evening tea-coffee breaks with cookies/savory snacks plus executive working buffet lunch", "per_person", 550.0, 30, ["corporate"], True),
        ("student_refreshments_catering", "catering", "Symposium Packed Meals & Welcome Refreshments", "Hygienic meal combo box with fruit juice, sandwich/biryani combo, snack bar, and water bottle", "per_person", 180.0, 50, ["college"], True),
        ("hydration_electrolyte_station", "catering", "Sports Hydration & Energy Station", "Unlimited mineral water dispensers, chilled electrolyte drinks, bananas, and glucose replenishment", "per_person", 80.0, 30, ["sports"], True),
        ("designer_custom_cake", "catering", "Custom Themed Fondant Birthday Cake (Per Kg)", "Custom handcrafted themed cake, premium flavors (Belgian chocolate, red velvet, butterscotch)", "per_item", 1400.0, 1, ["birthday"], False),

        # Photography
        ("candid_wedding_photography", "photography", "Premium Wedding Candid & Traditional Cinematography", "Full team: 2 Candid photographers, 2 Traditional videographers, drone aerials, luxury wedding album", "per_event", 65000.0, 1, ["wedding"], False),
        ("portrait_birthday_photography", "photography", "Birthday Event Photography & Reel Coverage", "4 hours candid shoot, candid video highlights, quick reel export for social media, digital album", "per_event", 12000.0, 1, ["birthday", "family_ceremonies"], False),
        ("corporate_conference_photography", "photography", "Corporate Photo & Video Documentation", "Full-day stage documentation, delegate networking shots, high-res PR photos, and wrap-up highlight reel", "per_day", 18000.0, 1, ["corporate", "college", "exhibition"], False),

        # Audio / Visual & Sound
        ("symposium_audio_pa_system", "sound", "Line-Array Audio PA System with Digital Mixer", "JBL/Yamaha line array speakers, stage monitors, 4 cordless handheld mics, 2 collar lapel mics", "per_day", 18000.0, 1, ["college", "corporate", "cultural", "entertainment"], True),
        ("audio_visual_projector_setup", "screens", "Dual 4K Laser Projectors & Motorized Screens", "High-lumen dual projectors suitable for brightly lit banquet halls, clickers, and HDMI switcher", "per_day", 14000.0, 1, ["corporate", "college"], False),
        ("led_video_wall_p3", "screens", "P3 High-Definition Indoor/Outdoor LED Screen (Per Sq Ft)", "Ultra high-definition LED video wall with Novastar video processor for live feeds and presentations", "per_item", 28000.0, 1, ["college", "cultural", "corporate", "entertainment"], False),
        ("theatre_lighting_rig", "lighting", "Stage Moving Heads & Ambience Par-Can Lighting", "Sharp moving head beams, LED warm wash pars, profile spotlights, DMX digital lighting controller", "per_day", 22000.0, 1, ["cultural", "wedding", "entertainment"], False),

        # Entertainment & Traditional Artists
        ("nadaswaram_tavil_troupe", "entertainment", "Traditional Nadaswaram & Thavil Troupe", "Senior artists performing auspicious classical ragas for 2 sessions (Muhurtham & Reception)", "per_event", 16000.0, 1, ["wedding", "cultural", "religious"], False),
        ("magic_show_or_mc", "entertainment", "Professional Master of Ceremonies (MC) & Party Host", "Bilingual English & Tamil interactive hosting, parlor magic, trivia quizzes, and crowd games", "per_event", 8000.0, 1, ["birthday", "corporate", "entertainment"], False),
        ("green_room_artist_hospitality", "manpower", "Artist Coordination & Green Room Setup", "Dedicated green room liaison, stage cues, makeup vanity lights, and hospitality management", "per_event", 9000.0, 1, ["cultural", "entertainment"], False),

        # Sports & Infrastructure
        ("tournament_ground_marking_equipment", "sports_gear", "Tournament Ground Markings, Nets & Referee Stands", "Professional boundary ropes, court lines, tournament-grade nets, scoreboards, and umpire gear", "per_day", 15000.0, 1, ["sports"], True),
        ("first_aid_medic_station", "manpower", "Certified Paramedic Station & First Aid Tent", "2 EMT paramedic staff, trauma kit, oxygen cylinder, stretcher, cold compression packs, physician liaison", "per_day", 10000.0, 1, ["sports", "college", "entertainment"], True),
        ("sports_championship_medals", "awards", "Championship Trophy Set & Embossed Medals", "1st/2nd/3rd large trophies, 30 gold/silver medals, personalized tournament ribbon bands", "per_event", 9500.0, 1, ["sports", "college"], False),
        ("trophies_certificates_pack", "awards", "Customized Mementos & Foil-Embossed Certificates", "Distinguished guest mementos, judge plaques, and 50 participant laminated certificates", "per_event", 7500.0, 1, ["college", "corporate"], False),

        # Logistics & Furniture
        ("banquet_cushion_chairs", "seating", "Comfortable Banquet Chairs with Fabric Slipcovers", "Clean padded banquet chairs with satin bow ties and clean linen", "per_seat", 45.0, 50, ["*"], False),
        ("registration_badging_desk", "registration", "Registration Desk with QR Badge Printing", "Dual laptop registration counters, thermal badge printers, lanyards, and 2 trained hostesses", "per_day", 11000.0, 1, ["corporate", "college", "exhibition"], False),
        ("event_coordinator_manager", "manpower", "Dedicated On-Site Event Coordinator", "Professional coordinator managing vendors, schedule, VIP arrivals, and contingency issues", "per_worker", 4000.0, 1, ["*"], False)
    ]

    service_models = {}
    for code, cat_code, name, desc, unit_type, base_price, min_qty, eligible_cats, is_mandatory in services_data:
        sc_id = svc_cat_models[cat_code].id
        svc = Service(
            service_category_id=sc_id,
            code=code,
            name=name,
            description=desc,
            unit_type=unit_type,
            base_price=base_price,
            min_quantity=min_qty,
            eligible_categories_json=json.dumps(eligible_cats),
            is_mandatory=is_mandatory,
            is_active=True
        )
        db.add(svc)
        db.flush()
        service_models[code] = svc

    # 5. Seed Category-Specific Packages (BASIC, STANDARD, PREMIUM for each category)
    packages_config = [
        # Wedding Packages
        ("wedding", "basic", "Sliver Muhurtham Package", "Essential arrangements for intimate traditional weddings up to 150 guests", 75000.0, 150,
         ["wedding_stage_decor", "traditional_banana_leaf_catering", "banquet_cushion_chairs"]),
        ("wedding", "standard", "Gold Heritage Wedding Package", "Complete wedding setup with catering, photography, and traditional music", 185000.0, 300,
         ["wedding_stage_decor", "traditional_banana_leaf_catering", "candid_wedding_photography", "nadaswaram_tavil_troupe", "banquet_cushion_chairs", "event_coordinator_manager"]),
        ("wedding", "premium", "Diamond Royal Kovai Wedding Gala", "Luxurious end-to-end wedding with full AV, multi-camera drone cinematography & VIP hospitality", 350000.0, 600,
         ["wedding_stage_decor", "traditional_banana_leaf_catering", "candid_wedding_photography", "nadaswaram_tavil_troupe", "theatre_lighting_rig", "banquet_cushion_chairs", "event_coordinator_manager"]),

        # Birthday Packages
        ("birthday", "basic", "Happy Moments Birthday Basic", "Cheerful birthday decor, cake and host for up to 30 guests", 25000.0, 30,
         ["birthday_theme_balloon_decor", "designer_custom_cake", "party_buffet_catering"]),
        ("birthday", "standard", "Carnival Joy Birthday Standard", "Full party experience with magic show MC, themed catering, and photo coverage", 48000.0, 60,
         ["birthday_theme_balloon_decor", "designer_custom_cake", "party_buffet_catering", "magic_show_or_mc", "portrait_birthday_photography"]),
        ("birthday", "premium", "Grand Fantasy Birthday Extravaganza", "Massive theme experience with live counters, customized 3D photo-booths and sound", 85000.0, 100,
         ["birthday_theme_balloon_decor", "designer_custom_cake", "party_buffet_catering", "magic_show_or_mc", "portrait_birthday_photography", "banquet_cushion_chairs", "event_coordinator_manager"]),

        # Corporate Packages
        ("corporate", "basic", "Executive Boardroom Seminar", "Essential AV and conference stage setup for business meetings", 45000.0, 50,
         ["corporate_conference_stage", "audio_visual_projector_setup", "corporate_high_tea_lunch"]),
        ("corporate", "standard", "Enterprise Summit Conference", "Professional conference setup with badging, photography, and high tea", 98000.0, 150,
         ["corporate_conference_stage", "audio_visual_projector_setup", "corporate_high_tea_lunch", "registration_badging_desk", "corporate_conference_photography", "symposium_audio_pa_system"]),
        ("corporate", "premium", "Flagship Industry Conclave", "Comprehensive corporate convention with LED video wall, PR media coverage & VIP lounge", 220000.0, 350,
         ["corporate_conference_stage", "audio_visual_projector_setup", "led_video_wall_p3", "corporate_high_tea_lunch", "registration_badging_desk", "corporate_conference_photography", "symposium_audio_pa_system", "event_coordinator_manager"]),

        # College Symposium Packages
        ("college", "basic", "Campus Department Symposium Basic", "Sound system, stage lectern, and student refreshments", 35000.0, 200,
         ["symposium_audio_pa_system", "student_refreshments_catering", "trophies_certificates_pack"]),
        ("college", "standard", "National Tech Fest Standard", "Auditorium sound, LED screen backdrop, stage decor, and guest awards", 85000.0, 500,
         ["symposium_audio_pa_system", "led_video_wall_p3", "student_refreshments_catering", "trophies_certificates_pack", "registration_badging_desk", "corporate_conference_stage"]),
        ("college", "premium", "Inter-Collegiate Mega Fest Premium", "Full campus festival with moving lights, pro PA, concert-grade LED & live stream", 175000.0, 1000,
         ["symposium_audio_pa_system", "led_video_wall_p3", "theatre_lighting_rig", "student_refreshments_catering", "trophies_certificates_pack", "registration_badging_desk", "event_coordinator_manager"]),

        # Cultural Packages
        ("cultural", "basic", "Arangetram & Classical Evening Basic", "Acoustic stage setup, traditional brass decor, and sound", 42000.0, 100,
         ["cultural_dance_stage_setup", "symposium_audio_pa_system", "banquet_cushion_chairs"]),
        ("cultural", "standard", "Isai Vizha & Natya Festival Standard", "Stage lighting, PA, green room management, and Tamil feast catering", 95000.0, 250,
         ["cultural_dance_stage_setup", "theatre_lighting_rig", "symposium_audio_pa_system", "green_room_artist_hospitality", "traditional_banana_leaf_catering"]),
        ("cultural", "premium", "Heritage Kala Mela Premium", "Multi-day festival setup with live streaming, master lighting, and full banquet", 190000.0, 500,
         ["cultural_dance_stage_setup", "theatre_lighting_rig", "led_video_wall_p3", "symposium_audio_pa_system", "green_room_artist_hospitality", "traditional_banana_leaf_catering", "event_coordinator_manager"]),

        # Sports Packages
        ("sports", "basic", "Local League Match Setup", "Ground marking, sports infrastructure, and hydration station", 28000.0, 50,
         ["tournament_ground_marking_equipment", "hydration_electrolyte_station", "first_aid_medic_station"]),
        ("sports", "standard", "Championship Tournament Standard", "Ground marking, medic tent, hydration, championship medals & sound setup", 58000.0, 150,
         ["tournament_ground_marking_equipment", "hydration_electrolyte_station", "first_aid_medic_station", "sports_championship_medals", "symposium_audio_pa_system"]),
        ("sports", "premium", "Coimbatore Corporate Sports Gala", "Full tournament management with live scoreboard, sound, trophy ceremony & event coordinator", 110000.0, 300,
         ["tournament_ground_marking_equipment", "hydration_electrolyte_station", "first_aid_medic_station", "sports_championship_medals", "symposium_audio_pa_system", "banquet_cushion_chairs", "event_coordinator_manager"])
    ]

    for cat_code, tier, name, desc, base_price, limit, svc_codes in packages_config:
        cat_model = category_models.get(cat_code)
        if not cat_model:
            continue
        pkg = EventPackage(
            category_id=cat_model.id,
            tier=tier,
            name=name,
            description=desc,
            base_price=base_price,
            attendee_limit=limit,
            is_active=True
        )
        db.add(pkg)
        db.flush()

        for scode in svc_codes:
            svc_obj = service_models.get(scode)
            if svc_obj:
                ps = PackageService(
                    package_id=pkg.id,
                    service_id=svc_obj.id,
                    included_quantity=1.0,
                    is_customizable=True
                )
                db.add(ps)

    # 6. Seed Coimbatore Venues (Sample Verified Data)
    sample_venues = [
        ("Kovai Mahal Kalyana Mandapam", "marriage_hall", "Peelamedu", 800, 75000.0, ["Central AC", "Dining Hall (300 seats)", "12 Guest Rooms", "Ample Car Parking"]),
        ("CODISSIA Trade Fair Complex Hall E", "convention_centre", "Avinashi Road", 2500, 180000.0, ["Acoustic Treatment", "Heavy Power Supply", "Exhibition Floor", "VIP Lounge"]),
        ("The Residency Towers Grand Ballroom", "hotel_banquet", "Avinashi Road", 350, 60000.0, ["Luxury Ambience", "In-house Catering", "Audio Visual Rig", "Valet Parking"]),
        ("RS Puram Club Banquet Hall", "hotel_banquet", "RS Puram", 200, 35000.0, ["Lawn Access", "Private Dining", "Bar Setup", "Centrally Located"]),
        ("PSG Tech Convention Auditorium", "college_campus", "Peelamedu", 1200, 50000.0, ["Tiered Seating", "Dolby Digital PA", "Green Rooms", "Green Campus"]),
        ("Siruvani Foothills Farm Retreat", "farm_resort", "Siruvani Road", 250, 45000.0, ["Scenic Mountain Backdrop", "Open Lawn", "Bonfire Pit", "Swimming Pool"]),
        ("Nehru Stadium Sports Complex", "public_ground", "Gandhipuram", 3000, 40000.0, ["Athletic Track", "Cricket Ground", "Floodlights", "Dressing Rooms"]),
        ("Vadavalli Community Hall", "community_hall", "Vadavalli", 300, 20000.0, ["Budget Friendly", "Kitchen Facility", "Community Friendly", "Bus Stop Proximity"])
    ]

    for vname, vtype, loc, cap, rate, amenities in sample_venues:
        venue = Venue(
            name=vname,
            venue_type=vtype,
            locality=loc,
            capacity=cap,
            base_day_rate=rate,
            amenities_json=json.dumps(amenities),
            is_verified=True
        )
        db.add(venue)

    # 7. Seed Sample Verified Coimbatore Vendors
    sample_vendors = [
        ("Subbiah Catering Services", "Subbiah Traditional Kovai Feasts", "Catering", "Gandhipuram", "+91 94433 11223", "subbiah@kovaimess.com", 4.9, "Starting from ₹350 per banana leaf meal"),
        ("Kavitha Decors & Events", "Kavitha Stage Artists & Floral Works", "Decoration", "RS Puram", "+91 98430 44556", "kavitha@kavithadecors.com", 4.8, "Stage decor from ₹25,000 onwards"),
        ("Kongu Studio Works", "Kongu Candid Wedding Cinematography", "Photography", "Peelamedu", "+91 99940 77889", "shoot@kongustudios.in", 4.9, "Photo & video packages from ₹45,000"),
        ("Sharp Audio Visuals Coimbatore", "Sharp Pro Audio & LED Wall Solutions", "Sound & AV", "Singanallur", "+91 98422 99001", "sound@sharpav.com", 4.7, "Line array & LED walls from ₹20,000"),
        ("Western Ghats Event Security", "Western Ghats Bouncers & Guest Liaison", "Security & Manpower", "Saravanampatti", "+91 97877 33445", "security@wgevent.com", 4.8, "Trained coordinators & security from ₹1,500/day")
    ]

    for vname, bname, vcat, loc, phone, email, rating, pr_desc in sample_vendors:
        vendor = Vendor(
            name=vname,
            business_name=bname,
            category=vcat,
            locality=loc,
            phone=phone,
            email=email,
            rating=rating,
            is_verified=True,
            sample_pricing_desc=pr_desc
        )
        db.add(vendor)

    db.commit()
    print("Database seeding completed successfully for Coimbatore EventMate AI!")
