// EventMate AI - Bilingual Localization (English & Tamil)
const translations = {
  en: {
    brand_subtitle: "Coimbatore",
    nav_home: "Home",
    nav_categories: "Event Categories",
    nav_packages: "Packages",
    nav_my_events: "My Dashboard",
    nav_admin: "Admin Console",
    nav_login: "Login / Register",
    nav_logout: "Logout",
    hero_tag: "Smart Coimbatore Event Engine",
    hero_title_1: "Every Celebration,",
    hero_title_2: "Planned Smarter.",
    hero_sub: "Plan weddings, birthdays, corporate events, college functions, cultural celebrations, and more with AI-powered recommendations, smart budgeting, and personalized event management in Coimbatore.",
    btn_plan_event: "Plan Your Event",
    btn_explore_packages: "Explore Packages",
    stat_localities: "Coimbatore Localities",
    stat_categories: "Event Categories",
    stat_vendors: "Verified Vendors",
    stat_ai_accuracy: "Budget Accuracy",
    section_cat_title: "Explore Event Categories",
    section_cat_sub: "Select an event category tailored for Coimbatore venues, traditions, and business needs.",
    btn_start_planning: "Start Planning →",
    wizard_step_1: "1. Event Details",
    wizard_step_2: "2. Category Info",
    wizard_step_3: "3. AI & Packages",
    wizard_step_4: "4. Quotation Preview",
    btn_back: "Back",
    btn_next: "Next Step",
    btn_generate_quote: "Generate Quotation",
    btn_approve_quote: "Approve Quotation",
    btn_request_change: "Request Changes",
    btn_pay_advance: "Pay Advance & Confirm",
    advance_notice: "25% Advance Booking Required"
  },
  ta: {
    brand_subtitle: "கோயம்புத்தூர்",
    nav_home: "முகப்பு",
    nav_categories: "நிகழ்வு வகைகள்",
    nav_packages: "தொகுப்புகள்",
    nav_my_events: "எனது நிகழ்வுகள்",
    nav_admin: "நிர்வாகக் குழு",
    nav_login: "உள்நுழைக / பதிவுசெய்க",
    nav_logout: "வெளியேறு",
    hero_tag: "கோவை ஸ்மார்ட் நிகழ்வு மேலாளர்",
    hero_title_1: "ஒவ்வொரு கொண்டாட்டமும்,",
    hero_title_2: "புத்திசாலித்தனமாகத் திட்டமிடுங்கள்.",
    hero_sub: "திருமணம், பிறந்தநாள், கார்ப்பரேட் நிகழ்வுகள், கல்லூரி விழாக்கள் மற்றும் கலாச்சார கொண்டாட்டங்களை AI பரிந்துரைகள் மற்றும் நேரடி பட்ஜெட் கணக்கீட்டுடன் கோவையில் எளிதாகத் திட்டமிடுங்கள்.",
    btn_plan_event: "உங்கள் நிகழ்வைத் திட்டமிடுங்கள்",
    btn_explore_packages: "தொகுப்புகளைப் பாருங்கள்",
    stat_localities: "கோவை பகுதிகள்",
    stat_categories: "நிகழ்வு வகைகள்",
    stat_vendors: "சரிபார்க்கப்பட்ட சேவையாளர்கள்",
    stat_ai_accuracy: "பட்ஜெட் துல்லியம்",
    section_cat_title: "நிகழ்வு வகைகளைத் தேர்வுசெய்க",
    section_cat_sub: "கோவையின் பிரத்யேக மண்டபங்கள், மரபுகள் மற்றும் நிறுவன தேவைகளுக்கு ஏற்ப வடிவமைக்கப்பட்ட பிரிவுகள்.",
    btn_start_planning: "திட்டமிடத் தொடங்குங்கள் →",
    wizard_step_1: "1. பொது விவரங்கள்",
    wizard_step_2: "2. பிரத்யேக தகவல்கள்",
    wizard_step_3: "3. AI & தொகுப்புகள்",
    wizard_step_4: "4. மதிப்பீட்டு அறிக்கை",
    btn_back: "முந்தையது",
    btn_next: "அடுத்த படி",
    btn_generate_quote: "விலை மதிப்பீடு பெறுக",
    btn_approve_quote: "ஒப்புதல் அளிக்கிறேன்",
    btn_request_change: "மாற்றங்கள் கோரவும்",
    btn_pay_advance: "முன்பணம் செலுத்தி உறுதிசெய்க",
    advance_notice: "25% முன்பதிவு தொகை தேவை"
  }
};

let currentLang = 'en';

function setLanguage(lang) {
  if (!translations[lang]) return;
  currentLang = lang;
  
  // Update all elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });

  // Toggle active class on buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
  });
  
  localStorage.setItem('eventmate_lang', lang);
}

function t(key) {
  return translations[currentLang][key] || key;
}

window.setLanguage = setLanguage;
window.t = t;
