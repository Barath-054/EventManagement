// EVENTMATE AI - Main Application Logic

let state = {
  currentUser: null,
  categories: [],
  selectedCategory: null,
  localities: [],
  venueTypes: [],
  currentWizardStep: 1,
  wizardData: {
    title: '',
    category_id: null,
    event_type_id: null,
    event_date: '',
    start_time: '09:00',
    end_time: '18:00',
    expected_attendees: 100,
    budget: 100000,
    preferred_locality: 'RS Puram',
    venue_type: 'hotel_banquet',
    indoor_outdoor: 'indoor',
    form_data: {},
    package_id: null,
    selectedServices: []
  },
  currentEvent: null,
  currentQuotation: null,
  currentBooking: null,
  userEvents: [],
  adminMetrics: null
};

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
  initLanguage();
  await loadInitialData();
  setupEventListeners();
  checkAuth();
});

function initLanguage() {
  const savedLang = localStorage.getItem('eventmate_lang') || 'en';
  window.setLanguage(savedLang);
}

async function loadInitialData() {
  try {
    const [cats, locs, venues] = await Promise.all([
      api.getCategories(),
      api.getLocalities(),
      api.getVenueTypes()
    ]);
    
    state.categories = cats;
    state.localities = locs.localities || [];
    state.venueTypes = venues.venue_types || [];
    
    renderCategoryCards();
    populateSelectDropdowns();
  } catch (err) {
    showToast('Failed to load initial platform data: ' + err.message, 'error');
  }
}

async function checkAuth() {
  if (api.token) {
    try {
      state.currentUser = await api.getMe();
      updateAuthUI();
      loadUserDashboard();
    } catch (e) {
      api.setToken(null);
      state.currentUser = null;
      updateAuthUI();
    }
  } else {
    updateAuthUI();
  }
}

function updateAuthUI() {
  const user = state.currentUser;
  const userGreeting = document.getElementById('user-greeting');
  const authBtn = document.getElementById('nav-auth-btn');
  const adminNavItem = document.getElementById('nav-admin-link');
  
  if (user) {
    userGreeting.textContent = `Hi, ${user.full_name.split(' ')[0]}`;
    userGreeting.style.display = 'inline-block';
    authBtn.textContent = t('nav_logout');
    authBtn.onclick = handleLogout;
    if (user.role === 'admin') {
      adminNavItem.style.display = 'inline-block';
    } else {
      adminNavItem.style.display = 'none';
    }
  } else {
    userGreeting.style.display = 'none';
    authBtn.textContent = t('nav_login');
    authBtn.onclick = () => openAuthModal();
    adminNavItem.style.display = 'none';
  }
}

function handleLogout() {
  api.setToken(null);
  state.currentUser = null;
  updateAuthUI();
  showToast('Logged out successfully', 'info');
  showView('home');
}

// Render Categories Grid on Landing Page
function renderCategoryCards() {
  const grid = document.getElementById('categories-grid');
  if (!grid) return;
  grid.innerHTML = '';

  const iconMap = {
    'wedding': '💍',
    'birthday': '🎂',
    'corporate': '💼',
    'college': '🎓',
    'cultural': '🎭',
    'religious': '🪔',
    'festival': '✨',
    'entertainment': '🎵',
    'sports': '🏆',
    'exhibition': '🏛️',
    'custom': '🎨'
  };

  state.categories.forEach(cat => {
    const icon = iconMap[cat.code] || '📅';
    const card = document.createElement('div');
    card.className = 'category-card';
    card.innerHTML = `
      <div class="cat-header">
        <div class="cat-icon-wrap">${icon}</div>
        <span class="badge badge-primary">${cat.event_types?.length || 5} types</span>
      </div>
      <h3 class="cat-title">${cat.name}</h3>
      <div class="cat-tamil-title">${cat.name_tamil || ''}</div>
      <p class="cat-desc">${cat.description || ''}</p>
      <div class="cat-footer">
        <span class="cat-subtype-count">Coimbatore Venues Ready</span>
        <button class="btn btn-sm btn-primary" onclick="startPlanningCategory(${cat.id})">
          ${t('btn_start_planning')}
        </button>
      </div>
    `;
    grid.appendChild(card);
  });
}

function populateSelectDropdowns() {
  const locSelect = document.getElementById('wiz-locality');
  if (locSelect) {
    locSelect.innerHTML = state.localities.map(loc => `<option value="${loc}">${loc}</option>`).join('');
    locSelect.value = 'RS Puram';
  }

  const venueSelect = document.getElementById('wiz-venue-type');
  if (venueSelect) {
    venueSelect.innerHTML = state.venueTypes.map(v => `<option value="${v.id}">${v.name}</option>`).join('');
  }
}

// -------------------------------------------------------------
// DYNAMIC EVENT PLANNING WIZARD
// -------------------------------------------------------------
window.startPlanningCategory = function(categoryId) {
  const cat = state.categories.find(c => c.id === categoryId);
  if (!cat) return;
  state.selectedCategory = cat;
  state.wizardData.category_id = cat.id;
  state.wizardData.title = `${cat.name.split('&')[0].trim()} Celebration`;
  
  // Set default budget and attendee according to category
  if (cat.code === 'wedding') {
    state.wizardData.budget = 250000;
    state.wizardData.expected_attendees = 300;
    state.wizardData.venue_type = 'marriage_hall';
    state.wizardData.preferred_locality = 'Peelamedu';
  } else if (cat.code === 'birthday') {
    state.wizardData.budget = 45000;
    state.wizardData.expected_attendees = 40;
    state.wizardData.venue_type = 'restaurant_party_hall';
    state.wizardData.preferred_locality = 'RS Puram';
  } else if (cat.code === 'corporate') {
    state.wizardData.budget = 120000;
    state.wizardData.expected_attendees = 150;
    state.wizardData.venue_type = 'conference_hall';
    state.wizardData.preferred_locality = 'Avinashi Road';
  } else if (cat.code === 'college') {
    state.wizardData.budget = 90000;
    state.wizardData.expected_attendees = 500;
    state.wizardData.venue_type = 'college_campus';
    state.wizardData.preferred_locality = 'Peelamedu';
  } else if (cat.code === 'sports') {
    state.wizardData.budget = 60000;
    state.wizardData.expected_attendees = 120;
    state.wizardData.venue_type = 'public_ground';
    state.wizardData.preferred_locality = 'Gandhipuram';
  } else {
    state.wizardData.budget = 80000;
    state.wizardData.expected_attendees = 100;
  }

  // Populate sub-types
  const subSelect = document.getElementById('wiz-event-subtype');
  if (subSelect && cat.event_types) {
    subSelect.innerHTML = cat.event_types.map(st => `<option value="${st.id}">${st.name} ${st.name_tamil ? `(${st.name_tamil})` : ''}</option>`).join('');
  }

  document.getElementById('wiz-title').value = state.wizardData.title;
  document.getElementById('wiz-attendees').value = state.wizardData.expected_attendees;
  document.getElementById('wiz-budget').value = state.wizardData.budget;
  document.getElementById('wiz-locality').value = state.wizardData.preferred_locality;
  document.getElementById('wiz-venue-type').value = state.wizardData.venue_type;
  
  // Set default event date (15 days from now)
  const d = new Date();
  d.setDate(d.getDate() + 15);
  document.getElementById('wiz-date').value = d.toISOString().split('T')[0];

  renderDynamicCategoryFields(cat);
  setWizardStep(1);
  openModal('wizard-modal');
};

function renderDynamicCategoryFields(cat) {
  const container = document.getElementById('wiz-dynamic-fields-container');
  if (!container) return;
  const code = cat.code.toLowerCase();

  let fieldsHtml = '';

  if (code === 'wedding') {
    fieldsHtml = `
      <div class="dynamic-fields-title">💍 Wedding & Muhurtham Traditions (Coimbatore)</div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Bride's Name</label>
          <input type="text" class="form-control dyn-input" data-key="bride_name" placeholder="e.g. Priya" value="Priya">
        </div>
        <div class="form-group">
          <label class="form-label">Groom's Name</label>
          <input type="text" class="form-control dyn-input" data-key="groom_name" placeholder="e.g. Rajesh" value="Rajesh">
        </div>
        <div class="form-group">
          <label class="form-label">Ceremony Tradition</label>
          <select class="form-control dyn-input" data-key="ceremony_type">
            <option value="Kongu Vellalar Traditional Muhurtham">Kongu Vellalar Traditional Muhurtham</option>
            <option value="Iyer / Iyengar Vaideeka Muhurtham">Iyer / Iyengar Vaideeka Muhurtham</option>
            <option value="Contemporary Fusion Wedding">Contemporary Fusion Wedding</option>
            <option value="Inter-Community Modern Wedding">Inter-Community Modern Wedding</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Muhurtham Auspicious Timing</label>
          <input type="text" class="form-control dyn-input" data-key="muhurtham_timing" value="06:00 AM - 07:30 AM" placeholder="e.g. 06:00 AM - 07:30 AM">
        </div>
        <div class="form-group form-group-full">
          <label class="form-label">Catering Tradition</label>
          <select class="form-control dyn-input" data-key="catering_tradition">
            <option value="Pure Kongu Vegetarian Banana Leaf">Pure Kongu Vegetarian Banana Leaf (24 Items)</option>
            <option value="Traditional Multi-Course Feast">Traditional Multi-Course Feast</option>
            <option value="Evening Grand Reception Buffet">Evening Grand Reception Buffet</option>
          </select>
        </div>
      </div>
    `;
  } else if (code === 'birthday') {
    fieldsHtml = `
      <div class="dynamic-fields-title">🎂 Birthday Party Preferences</div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Celebrant Age</label>
          <input type="text" class="form-control dyn-input" data-key="age" value="5 years" placeholder="e.g. 1st Birthday, 5 years, 25th milestone">
        </div>
        <div class="form-group">
          <label class="form-label">Party Theme</label>
          <input type="text" class="form-control dyn-input" data-key="party_theme" value="Avengers Superhero / Fairy Tale" placeholder="e.g. Boss Baby, Avengers, Neon Glow">
        </div>
        <div class="form-group">
          <label class="form-label">Cake Flavor & Size</label>
          <input type="text" class="form-control dyn-input" data-key="cake_flavor" value="Belgian Chocolate Fondant (3 Kg)">
        </div>
        <div class="form-group">
          <label class="form-label">Entertainment / Games</label>
          <input type="text" class="form-control dyn-input" data-key="games_needed" value="Magic show, MC host, balloon twisting">
        </div>
      </div>
    `;
  } else if (code === 'corporate') {
    fieldsHtml = `
      <div class="dynamic-fields-title">💼 Corporate & Conference Setup</div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Organization / Company Name</label>
          <input type="text" class="form-control dyn-input" data-key="company_name" value="Kongu Tech Innovations Pvt Ltd">
        </div>
        <div class="form-group">
          <label class="form-label">Event Objective</label>
          <input type="text" class="form-control dyn-input" data-key="event_objective" value="Annual Tech Leadership & Product Showcase">
        </div>
        <div class="form-group">
          <label class="form-label">AV / Projector Equipment</label>
          <input type="text" class="form-control dyn-input" data-key="av_gear" value="Dual 4K Laser Projectors + Collar Lapel Mics">
        </div>
        <div class="form-group">
          <label class="form-label">Registration & Badging Desks</label>
          <input type="number" class="form-control dyn-input" data-key="registration_booths" value="2">
        </div>
      </div>
    `;
  } else if (code === 'college') {
    fieldsHtml = `
      <div class="dynamic-fields-title">🎓 College Symposium & Fest Arrangements</div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Institution Name</label>
          <input type="text" class="form-control dyn-input" data-key="institution" value="Coimbatore Institute of Engineering">
        </div>
        <div class="form-group">
          <label class="form-label">Department / Club</label>
          <input type="text" class="form-control dyn-input" data-key="department" value="Computer Science & Engineering">
        </div>
        <div class="form-group">
          <label class="form-label">Competition Track Count</label>
          <input type="number" class="form-control dyn-input" data-key="competition_count" value="8">
        </div>
        <div class="form-group">
          <label class="form-label">Awards & Certificates</label>
          <input type="text" class="form-control dyn-input" data-key="awards_needed" value="Championship mementos and certificates">
        </div>
      </div>
    `;
  } else if (code === 'cultural') {
    fieldsHtml = `
      <div class="dynamic-fields-title">🎭 Cultural & Traditional Performance Requirements</div>
      <div class="form-grid">
        <div class="form-group form-group-full">
          <label class="form-label">Performance Types</label>
          <input type="text" class="form-control dyn-input" data-key="performances" value="Bharatanatyam Recital + Carnatic Vocal Troupe">
        </div>
        <div class="form-group">
          <label class="form-label">Green Room & Backstage Required?</label>
          <select class="form-control dyn-input" data-key="green_room_required">
            <option value="Yes - Dedicated Separate Green Rooms">Yes - Dedicated Separate Green Rooms</option>
            <option value="No">No</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Lighting Rig</label>
          <input type="text" class="form-control dyn-input" data-key="lighting_profile" value="Theatre profile spot + Warm par washes">
        </div>
      </div>
    `;
  } else if (code === 'sports') {
    fieldsHtml = `
      <div class="dynamic-fields-title">🏆 Sports Tournament Operations</div>
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Sport Discipline</label>
          <input type="text" class="form-control dyn-input" data-key="sport_type" value="Cricket T10 / Football League">
        </div>
        <div class="form-group">
          <label class="form-label">Number of Participating Teams</label>
          <input type="number" class="form-control dyn-input" data-key="teams" value="16">
        </div>
        <div class="form-group">
          <label class="form-label">Medic & First Aid Support</label>
          <input type="text" class="form-control dyn-input" data-key="first_aid" value="Paramedic staff on field with cold packs">
        </div>
        <div class="form-group">
          <label class="form-label">Hydration & Refreshments</label>
          <input type="text" class="form-control dyn-input" data-key="electrolyte_stations" value="Electrolytes & Mineral Water Dispensers">
        </div>
      </div>
    `;
  } else {
    // Custom / Religious / Festival generic setup
    fieldsHtml = `
      <div class="dynamic-fields-title">✨ Bespoke & Tradition Arrangements</div>
      <div class="form-grid">
        <div class="form-group form-group-full">
          <label class="form-label">Specific Event Purpose & Theme</label>
          <textarea class="form-control dyn-input" data-key="custom_purpose" rows="2" placeholder="Specify any unique pooja rules, rituals, or themes"></textarea>
        </div>
        <div class="form-group form-group-full">
          <label class="form-label">Special Ingress or Venue Requests</label>
          <input type="text" class="form-control dyn-input" data-key="special_needs" placeholder="e.g. Fire pit clearance, VIP entrance, generator backup">
        </div>
      </div>
    `;
  }

  container.innerHTML = fieldsHtml;
}

function setWizardStep(step) {
  state.currentWizardStep = step;
  
  // Update step indicators
  document.querySelectorAll('.wizard-step').forEach((el, index) => {
    const stepNum = index + 1;
    el.classList.toggle('active', stepNum === step);
    el.classList.toggle('completed', stepNum < step);
  });

  // Toggle step panes
  document.getElementById('wiz-step-1').style.display = (step === 1) ? 'block' : 'none';
  document.getElementById('wiz-step-2').style.display = (step === 2) ? 'block' : 'none';
  document.getElementById('wiz-step-3').style.display = (step === 3) ? 'block' : 'none';
  document.getElementById('wiz-step-4').style.display = (step === 4) ? 'block' : 'none';

  // Update footer buttons
  const backBtn = document.getElementById('wiz-back-btn');
  const nextBtn = document.getElementById('wiz-next-btn');

  backBtn.style.display = (step === 1) ? 'none' : 'inline-flex';
  if (step === 4) {
    nextBtn.textContent = 'Save & Generate Quotation';
    nextBtn.className = 'btn btn-primary';
  } else {
    nextBtn.textContent = t('btn_next');
    nextBtn.className = 'btn btn-primary';
  }
}

window.wizardNextStep = async function() {
  if (state.currentWizardStep === 1) {
    // Collect step 1
    state.wizardData.title = document.getElementById('wiz-title').value;
    state.wizardData.event_date = document.getElementById('wiz-date').value;
    state.wizardData.expected_attendees = parseInt(document.getElementById('wiz-attendees').value) || 50;
    state.wizardData.budget = parseFloat(document.getElementById('wiz-budget').value) || 50000;
    state.wizardData.preferred_locality = document.getElementById('wiz-locality').value;
    state.wizardData.venue_type = document.getElementById('wiz-venue-type').value;
    state.wizardData.indoor_outdoor = document.getElementById('wiz-indoor-outdoor').value;
    
    setWizardStep(2);
  } 
  else if (state.currentWizardStep === 2) {
    // Collect step 2 dynamic inputs
    const dynInputs = document.querySelectorAll('.dyn-input');
    state.wizardData.form_data = {};
    dynInputs.forEach(inp => {
      const k = inp.getAttribute('data-key');
      state.wizardData.form_data[k] = inp.value;
    });

    // Load Packages & Run AI Recommendations for Step 3
    await loadStep3AIAndPackages();
    setWizardStep(3);
  }
  else if (state.currentWizardStep === 3) {
    // Calculate live pricing preview for Step 4
    await prepareStep4Preview();
    setWizardStep(4);
  }
  else if (state.currentWizardStep === 4) {
    // Submit event & create formal quotation
    await finalizeEventAndQuotation();
  }
};

window.wizardPrevStep = function() {
  if (state.currentWizardStep > 1) {
    setWizardStep(state.currentWizardStep - 1);
  }
};

async function loadStep3AIAndPackages() {
  const cat = state.selectedCategory;
  const packagesContainer = document.getElementById('wiz-packages-container');
  const aiStudioContainer = document.getElementById('wiz-ai-studio');

  packagesContainer.innerHTML = '<div style="color: var(--text-muted);">Loading packages...</div>';
  aiStudioContainer.innerHTML = '<div style="color: var(--text-muted);">Running AI Event Analysis...</div>';

  try {
    // 1. Fetch Packages
    const pkgs = await api.getPackages(cat.id);
    if (pkgs.length === 0) {
      packagesContainer.innerHTML = '<div style="color: var(--text-muted);">Custom package tier will be tailored below.</div>';
    } else {
      packagesContainer.innerHTML = pkgs.map((p, idx) => `
        <div class="package-card ${idx === 1 ? 'selected' : ''}" onclick="selectPackage(${p.id}, this)">
          <div>
            <span class="package-tier-badge tier-${p.tier.toLowerCase()}">${p.tier}</span>
            <h4>${p.name}</h4>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">${p.description || ''}</p>
          </div>
          <div class="package-price">₹${p.base_price.toLocaleString('en-IN')}</div>
          <div style="font-size: 0.78rem; color: var(--text-dim);">${p.included_services?.length || 3} Included Services</div>
        </div>
      `).join('');
      // Default to standard package if available
      const standardPkg = pkgs.find(p => p.tier === 'standard') || pkgs[0];
      state.wizardData.package_id = standardPkg.id;
    }

    // 2. Fetch AI Recommendations
    const aiRes = await api.analyzeEvent({
      category_id: cat.id,
      category_code: cat.code,
      attendees: state.wizardData.expected_attendees,
      budget: state.wizardData.budget,
      venue_type: state.wizardData.venue_type,
      preferred_locality: state.wizardData.preferred_locality,
      indoor_outdoor: state.wizardData.indoor_outdoor,
      form_data: state.wizardData.form_data
    });

    renderAIStudio(aiRes);
    // Initialize selected services with AI recommendations
    state.wizardData.selectedServices = aiRes.recommendations.map(r => ({
      service_id: r.service_id,
      service_name: r.service_name,
      quantity: r.suggested_quantity,
      unit_type: r.unit_type,
      unit_price: r.unit_price,
      estimated_cost: r.estimated_cost
    }));

  } catch (err) {
    aiStudioContainer.innerHTML = `<div style="color: var(--danger);">Failed to load recommendations: ${err.message}</div>`;
  }
}

function selectPackage(pkgId, el) {
  state.wizardData.package_id = pkgId;
  document.querySelectorAll('.package-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
}

function renderAIStudio(aiRes) {
  const container = document.getElementById('wiz-ai-studio');
  if (!container) return;

  const scoreColor = aiRes.is_within_budget ? '#34d399' : '#f59e0b';

  container.innerHTML = `
    <div class="ai-header">
      <div>
        <h4 style="display: flex; align-items: center; gap: 8px;">
          🤖 EventMate AI Recommendation Studio
          <span class="badge ${aiRes.is_within_budget ? 'badge-primary' : 'badge-accent'}">${aiRes.feasibility_status}</span>
        </h4>
        <p style="font-size: 0.88rem; color: var(--text-muted); margin-top: 4px;">${aiRes.explanation}</p>
      </div>
      <div class="ai-score-pill" style="border-color: ${scoreColor}; color: ${scoreColor};">
        Score: ${aiRes.feasibility_score}%
      </div>
    </div>

    <!-- Coimbatore Localized Advisory -->
    <div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid var(--accent); padding: 0.75rem 1rem; border-radius: 6px; font-size: 0.85rem; margin-bottom: 1.25rem;">
      <strong>📍 Coimbatore Locality Insight:</strong> ${aiRes.coimbatore_venue_advice}
    </div>

    <!-- Recommended Services with Transparent Rationale -->
    <h5 style="margin-bottom: 0.75rem; font-size: 0.95rem;">Recommended Priority Arrangements:</h5>
    <div class="ai-items-list">
      ${aiRes.recommendations.map(r => `
        <div class="ai-item-card">
          <div style="flex-grow: 1;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <strong>${r.service_name}</strong>
              <span class="badge ${r.priority === 'Essential' ? 'badge-primary' : 'badge-secondary'}">${r.priority}</span>
            </div>
            <div class="ai-item-reason">💡 <em>Why:</em> ${r.reason}</div>
            <div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 4px;">
              Qty: ${r.suggested_quantity} ${r.unit_type.replace('_', ' ')} @ ₹${r.unit_price.toLocaleString('en-IN')}
            </div>
          </div>
          <div style="text-align: right; font-weight: 700; color: #ffffff;">
            ₹${r.estimated_cost.toLocaleString('en-IN')}
          </div>
        </div>
      `).join('')}
    </div>

    ${aiRes.cost_saving_tips && aiRes.cost_saving_tips.length > 0 ? `
      <div style="margin-top: 1.25rem; background: rgba(99, 102, 241, 0.08); border: 1px dashed rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 1rem;">
        <h6 style="color: #818cf8; margin-bottom: 0.5rem;">💡 Smart Cost-Saving Alternatives:</h6>
        <ul style="font-size: 0.84rem; color: var(--text-muted); padding-left: 1.2rem;">
          ${aiRes.cost_saving_tips.map(tip => `<li>${tip}</li>`).join('')}
        </ul>
      </div>
    ` : ''}
  `;
}

async function prepareStep4Preview() {
  const previewWrap = document.getElementById('wiz-step-4-preview');
  previewWrap.innerHTML = '<div style="color: var(--text-muted);">Calculating line items and taxes...</div>';

  const previewRes = await api.previewQuotation({
    attendees: state.wizardData.expected_attendees,
    services: state.wizardData.selectedServices.map(s => ({
      service_id: s.service_id,
      quantity: s.quantity
    }))
  });

  state.currentQuotation = previewRes;

  previewWrap.innerHTML = `
    <div class="quote-table-wrap">
      <table class="custom-table">
        <thead>
          <tr>
            <th>Service Arrangement</th>
            <th>Pricing Unit</th>
            <th>Quantity</th>
            <th>Rate (₹)</th>
            <th style="text-align: right;">Total (₹)</th>
          </tr>
        </thead>
        <tbody>
          ${previewRes.items.map(itm => `
            <tr>
              <td>
                <strong>${itm.service_name}</strong>
                <div style="font-size: 0.78rem; color: var(--text-dim);">${itm.category_name}</div>
              </td>
              <td><span class="badge badge-secondary">${itm.unit_type.replace('_', ' ')}</span></td>
              <td>${itm.quantity}</td>
              <td>₹${itm.unit_price.toLocaleString('en-IN')}</td>
              <td style="text-align: right; font-weight: 700;">₹${itm.total_price.toLocaleString('en-IN')}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>

    <div class="quote-totals-box">
      <div class="quote-row">
        <span>Service Subtotal:</span>
        <span>₹${previewRes.subtotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
      </div>
      <div class="quote-row">
        <span>Coimbatore GST (18% - 9% CGST + 9% SGST):</span>
        <span>₹${previewRes.tax_amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
      </div>
      <div class="quote-row grand-total">
        <span>Estimated Grand Total:</span>
        <span style="color: var(--primary);">₹${previewRes.grand_total.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
      </div>
      <div class="quote-row advance-row">
        <span>25% Advance Booking Required:</span>
        <span>₹${previewRes.advance_required.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
      </div>
    </div>
  `;
}

async function finalizeEventAndQuotation() {
  if (!state.currentUser) {
    showToast('Please login to save and confirm your event.', 'info');
    openAuthModal();
    return;
  }

  try {
    // 1. Create Event
    const eventPayload = {
      category_id: state.wizardData.category_id,
      title: state.wizardData.title,
      event_date: state.wizardData.event_date,
      start_time: state.wizardData.start_time,
      end_time: state.wizardData.end_time,
      expected_attendees: state.wizardData.expected_attendees,
      budget: state.wizardData.budget,
      venue_type: state.wizardData.venue_type,
      preferred_locality: state.wizardData.preferred_locality,
      indoor_outdoor: state.wizardData.indoor_outdoor,
      form_data: state.wizardData.form_data,
      package_id: state.wizardData.package_id,
      services: state.wizardData.selectedServices.map(s => ({
        service_id: s.service_id,
        quantity: s.quantity
      }))
    };

    const createdEvent = await api.createEvent(eventPayload);
    state.currentEvent = createdEvent;

    // 2. Generate Quotation
    const generatedQuote = await api.generateQuotation({
      event_id: createdEvent.id,
      services: state.wizardData.selectedServices.map(s => ({
        service_id: s.service_id,
        quantity: s.quantity
      }))
    });

    state.currentQuotation = generatedQuote;
    closeModal('wizard-modal');
    showToast('Quotation generated successfully!', 'success');

    // Open formal Quotation modal
    openQuotationModal(generatedQuote);
    loadUserDashboard();

  } catch (err) {
    showToast('Failed to generate quotation: ' + err.message, 'error');
  }
}

// -------------------------------------------------------------
// FORMAL QUOTATION MODAL & ACTIONS
// -------------------------------------------------------------
window.openQuotationModal = function(quote) {
  state.currentQuotation = quote;
  const body = document.getElementById('quotation-modal-body');
  
  body.innerHTML = `
    <div id="quotation-print-container">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid var(--border-color); padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
        <div>
          <h2 style="font-size: 1.8rem; color: #ffffff;">EVENTMATE AI</h2>
          <div style="font-size: 0.85rem; color: var(--accent);">Smart Event Management Platform - Coimbatore, TN</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">GSTIN: 33AABCS1429E1Z2 | support@eventmate.ai</div>
        </div>
        <div style="text-align: right;">
          <div class="badge badge-primary" style="font-size: 0.9rem; padding: 0.35rem 0.8rem;">${quote.quotation_number}</div>
          <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 6px;">Version: ${quote.version} | Status: <strong style="text-transform: uppercase;">${quote.status}</strong></div>
          <div style="font-size: 0.8rem; color: var(--text-dim);">Valid Until: ${quote.valid_until}</div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; background: var(--bg-input); padding: 1rem 1.25rem; border-radius: 8px;">
        <div>
          <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted);">Event Name & Category</div>
          <strong style="color: #ffffff; font-size: 1.05rem;">${quote.event_title || state.wizardData.title}</strong>
          <div style="font-size: 0.85rem; color: var(--primary);">${quote.category_name}</div>
        </div>
        <div>
          <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted);">Customer & Locality</div>
          <strong style="color: #ffffff;">${state.currentUser ? state.currentUser.full_name : 'Customer'}</strong>
          <div style="font-size: 0.85rem; color: var(--text-muted);">${state.wizardData.preferred_locality}, Coimbatore</div>
        </div>
      </div>

      <div class="quote-table-wrap">
        <table class="custom-table quote-table">
          <thead>
            <tr>
              <th>Service Arrangement</th>
              <th>Category</th>
              <th>Unit</th>
              <th>Qty</th>
              <th>Rate (₹)</th>
              <th style="text-align: right;">Total (₹)</th>
            </tr>
          </thead>
          <tbody>
            ${quote.items.map(itm => `
              <tr>
                <td><strong>${itm.service_name}</strong></td>
                <td><span class="badge badge-secondary">${itm.category_name}</span></td>
                <td>${itm.unit_type.replace('_', ' ')}</td>
                <td>${itm.quantity}</td>
                <td>₹${itm.unit_price.toLocaleString('en-IN')}</td>
                <td style="text-align: right; font-weight: 700;">₹${itm.total_price.toLocaleString('en-IN')}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="quote-totals-box">
        <div class="quote-row">
          <span>Subtotal:</span>
          <span>₹${quote.subtotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
        </div>
        <div class="quote-row">
          <span>CGST (9%):</span>
          <span>₹${(quote.tax_amount / 2).toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
        </div>
        <div class="quote-row">
          <span>SGST (9%):</span>
          <span>₹${(quote.tax_amount / 2).toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
        </div>
        <div class="quote-row grand-total">
          <span>Quotation Grand Total:</span>
          <span style="color: var(--primary);">₹${quote.grand_total.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
        </div>
        <div class="quote-row advance-row">
          <span>Advance Booking Amount Due:</span>
          <span>₹${quote.advance_required.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
        </div>
      </div>
    </div>
  `;

  // Action Buttons
  const footer = document.getElementById('quotation-modal-footer');
  const isApproved = quote.status === 'approved' || quote.status === 'booked';
  
  footer.innerHTML = `
    <div>
      <button class="btn btn-secondary no-print" onclick="window.print()">🖨️ Print / Download PDF</button>
    </div>
    <div style="display: flex; gap: 0.75rem;">
      ${!isApproved ? `
        <button class="btn btn-secondary" onclick="openRevisionDialog(${quote.id})">Request Changes</button>
        <button class="btn btn-primary" onclick="handleApproveQuotation(${quote.id})">Approve Quotation</button>
      ` : `
        <button class="btn btn-accent" onclick="openPaymentModal(${quote.id}, ${quote.advance_required})">
          💳 Pay 25% Advance (₹${quote.advance_required.toLocaleString('en-IN')})
        </button>
      `}
    </div>
  `;

  openModal('quotation-modal');
};

window.handleApproveQuotation = async function(quoteId) {
  try {
    const updated = await api.approveQuotation(quoteId);
    showToast('Quotation successfully approved! You can now proceed with advance booking.', 'success');
    openQuotationModal(updated);
    loadUserDashboard();
  } catch (err) {
    showToast('Failed to approve quotation: ' + err.message, 'error');
  }
};

window.openRevisionDialog = function(quoteId) {
  const reason = prompt('Please specify the changes or service adjustments you would like to request:');
  if (!reason) return;
  
  api.requestQuotationChange(quoteId, { reason })
    .then(updated => {
      showToast('Quotation revision requested. Our team will review the adjustment.', 'info');
      openQuotationModal(updated);
    })
    .catch(err => showToast(err.message, 'error'));
};

// -------------------------------------------------------------
// ADVANCE PAYMENT GATEWAY SIMULATION
// -------------------------------------------------------------
window.openPaymentModal = function(quoteId, amount) {
  document.getElementById('pay-amount-display').textContent = `₹${amount.toLocaleString('en-IN')}`;
  document.getElementById('pay-quote-id').value = quoteId;
  openModal('payment-modal');
};

window.handlePaymentSubmit = async function(event) {
  event.preventDefault();
  const quoteId = parseInt(document.getElementById('pay-quote-id').value);
  const method = document.querySelector('input[name="payment_method"]:checked').value;
  const upiId = document.getElementById('pay-upi-id')?.value || 'customer@okaxis';

  const btn = document.getElementById('pay-submit-btn');
  btn.disabled = true;
  btn.textContent = 'Processing Payment...';

  try {
    const res = await api.processAdvancePayment({
      quotation_id: quoteId,
      payment_type: 'advance',
      payment_method: method,
      upi_id: upiId
    });

    closeModal('payment-modal');
    closeModal('quotation-modal');
    showToast(`Payment Confirmed! Ref: ${res.transaction_reference}`, 'success');

    // Open Tracking View
    await viewBookingByEvent(state.currentEvent ? state.currentEvent.id : null);
    loadUserDashboard();

  } catch (err) {
    showToast('Payment failed: ' + err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Confirm & Pay Advance';
  }
};

// -------------------------------------------------------------
// EVENT EXECUTION TRACKING & TASKS
// -------------------------------------------------------------
window.viewBookingByEvent = async function(eventId) {
  if (!eventId) {
    showToast('Please select an active event first.', 'info');
    return;
  }
  try {
    const booking = await api.getBookingByEvent(eventId);
    state.currentBooking = booking;
    renderTrackingView(booking);
    showView('tracking');
  } catch (err) {
    showToast('Booking details not available yet. Please complete advance payment.', 'info');
  }
};

function renderTrackingView(booking) {
  const container = document.getElementById('tracking-container');
  if (!container) return;

  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <div>
        <span class="badge badge-primary">Booking Reference: ${booking.booking_reference}</span>
        <h2 style="margin-top: 0.5rem;">${booking.event_title}</h2>
        <div style="color: var(--text-muted); font-size: 0.9rem;">Category: ${booking.category_name} | Advance Paid: ₹${booking.advance_paid.toLocaleString('en-IN')}</div>
      </div>
      <div>
        <button class="btn btn-secondary" onclick="openReviewModal(${booking.event_id})">⭐ Submit Feedback</button>
      </div>
    </div>

    <!-- Stepper -->
    <div class="tracking-stepper">
      <div class="track-step done">
        <div class="track-circle">✓</div>
        <span style="font-size: 0.8rem; font-weight: 600;">Booking Confirmed</span>
      </div>
      <div class="track-step done">
        <div class="track-circle">✓</div>
        <span style="font-size: 0.8rem; font-weight: 600;">Advance Verified</span>
      </div>
      <div class="track-step current">
        <div class="track-circle">3</div>
        <span style="font-size: 0.8rem; font-weight: 600;">Vendor Ingress</span>
      </div>
      <div class="track-step">
        <div class="track-circle">4</div>
        <span style="font-size: 0.8rem; font-weight: 600;">Event Execution</span>
      </div>
      <div class="track-step">
        <div class="track-circle">5</div>
        <span style="font-size: 0.8rem; font-weight: 600;">Wrap-up & Review</span>
      </div>
    </div>

    <!-- Interactive Execution Checklist -->
    <h3 style="margin: 2rem 0 1rem;">Execution Milestones & Logistics Checklist:</h3>
    <div class="task-list">
      ${booking.tasks.map(t => `
        <div class="task-item ${t.status === 'completed' ? 'completed' : ''}">
          <div style="display: flex; align-items: center; gap: 12px;">
            <input type="checkbox" ${t.status === 'completed' ? 'checked' : ''} onchange="toggleTaskStatus(${booking.id}, ${t.id}, this.checked)">
            <div>
              <div class="task-title" style="${t.status === 'completed' ? 'text-decoration: line-through;' : ''}">${t.title}</div>
              <div class="task-meta">Assigned: ${t.assigned_to} | Target: ${t.due_date || 'N/A'}</div>
            </div>
          </div>
          <span class="badge ${t.status === 'completed' ? 'badge-primary' : 'badge-secondary'}">${t.status}</span>
        </div>
      `).join('')}
    </div>
  `;
}

window.toggleTaskStatus = async function(bookingId, taskId, isChecked) {
  try {
    const newStatus = isChecked ? 'completed' : 'pending';
    await api.updateTaskStatus(bookingId, taskId, newStatus);
    showToast(`Task marked as ${newStatus}`, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
};

// -------------------------------------------------------------
// POST-EVENT REVIEW MODAL
// -------------------------------------------------------------
window.openReviewModal = function(eventId) {
  document.getElementById('review-event-id').value = eventId;
  openModal('review-modal');
};

window.handleReviewSubmit = async function(e) {
  e.preventDefault();
  const eventId = parseInt(document.getElementById('review-event-id').value);
  const rating = parseInt(document.getElementById('review-rating').value);
  const feedback = document.getElementById('review-feedback').value;

  try {
    await api.submitReview({
      event_id: eventId,
      rating: rating,
      title: 'Customer Feedback',
      feedback_text: feedback
    });
    closeModal('review-modal');
    showToast('Thank you for your valuable feedback!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
};

// -------------------------------------------------------------
// CUSTOMER & ADMIN DASHBOARDS
// -------------------------------------------------------------
async function loadUserDashboard() {
  if (!state.currentUser) return;
  try {
    const events = await api.getEvents();
    state.userEvents = events;
    renderUserDashboard(events);
  } catch (err) {
    console.error('Failed to load user events:', err);
  }
}

function renderUserDashboard(events) {
  const container = document.getElementById('user-events-list');
  if (!container) return;

  if (events.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
        <p>You haven't planned any events yet.</p>
        <button class="btn btn-primary" style="margin-top: 1rem;" onclick="showView('home')">Plan an Event Now</button>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem;">
      ${events.map(ev => `
        <div class="glass-panel" style="padding: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
            <span class="badge badge-secondary">${ev.category_name}</span>
            <span class="badge ${ev.status === 'booked' ? 'badge-primary' : 'badge-accent'}">${ev.status.toUpperCase()}</span>
          </div>
          <h4>${ev.title}</h4>
          <div style="font-size: 0.85rem; color: var(--text-muted); margin: 0.5rem 0 1rem;">
            📅 ${ev.event_date || 'Flexible'} | 👥 ${ev.expected_attendees} guests | 📍 ${ev.preferred_locality}
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 0.75rem;">
            <strong style="color: var(--primary);">₹${ev.budget.toLocaleString('en-IN')}</strong>
            <button class="btn btn-sm btn-primary" onclick="viewBookingByEvent(${ev.id})">Track Status →</button>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

window.loadAdminDashboard = async function() {
  if (!state.currentUser || state.currentUser.role !== 'admin') {
    showToast('Administrator privileges required.', 'error');
    return;
  }

  try {
    const metrics = await api.getAdminMetrics();
    state.adminMetrics = metrics;

    document.getElementById('metric-total-events').textContent = metrics.total_events;
    document.getElementById('metric-total-bookings').textContent = metrics.total_bookings;
    document.getElementById('metric-pending-quotes').textContent = metrics.pending_quotations;
    document.getElementById('metric-revenue').textContent = `₹${metrics.total_revenue_collected.toLocaleString('en-IN')}`;

    // Load filterable events
    const events = await api.getAdminEvents();
    const tableBody = document.getElementById('admin-events-table-body');
    if (tableBody) {
      tableBody.innerHTML = events.map(e => `
        <tr>
          <td><strong>${e.title}</strong></td>
          <td><span class="badge badge-secondary">${e.category_name}</span></td>
          <td>${e.user_name} (${e.user_email})</td>
          <td>${e.preferred_locality}</td>
          <td>${e.attendees}</td>
          <td>₹${e.budget.toLocaleString('en-IN')}</td>
          <td><span class="badge ${e.status === 'booked' ? 'badge-primary' : 'badge-accent'}">${e.status}</span></td>
        </tr>
      `).join('');
    }

    showView('admin');
  } catch (err) {
    showToast('Failed to load admin metrics: ' + err.message, 'error');
  }
};

// -------------------------------------------------------------
// ONE-CLICK TEST WORKFLOWS RUNNER (FOR CONVENIENT TESTING)
// -------------------------------------------------------------
window.runDemoWorkflow = async function(workflowType) {
  showToast(`Initiating automated demo test: ${workflowType.toUpperCase()}`, 'info');

  const catCodeMap = {
    'wedding': 'wedding',
    'birthday': 'birthday',
    'corporate': 'corporate',
    'college': 'college',
    'cultural': 'cultural',
    'sports': 'sports',
    'custom': 'custom'
  };

  const targetCode = catCodeMap[workflowType];
  const targetCat = state.categories.find(c => c.code === targetCode);
  if (!targetCat) {
    showToast('Category not found for demo.', 'error');
    return;
  }

  // Pre-fill and start wizard
  startPlanningCategory(targetCat.id);
};

// -------------------------------------------------------------
// UTILITY HELPERS & VIEW CONTROLLERS
// -------------------------------------------------------------
window.showView = function(viewName) {
  document.querySelectorAll('.dashboard-view').forEach(v => v.classList.remove('active'));
  const el = document.getElementById(`view-${viewName}`);
  if (el) el.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

window.openModal = function(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('active');
};

window.closeModal = function(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('active');
};

function openAuthModal() {
  openModal('auth-modal');
}

window.handleAuthSubmit = async function(e) {
  e.preventDefault();
  const email = document.getElementById('auth-email').value;
  const password = document.getElementById('auth-password').value;
  const isRegister = document.getElementById('auth-is-register').checked;
  const name = document.getElementById('auth-name').value;

  try {
    let res;
    if (isRegister) {
      res = await api.register({
        full_name: name || 'Valued Client',
        email,
        password,
        role: 'customer'
      });
      showToast('Registration successful! Welcome to EventMate AI.', 'success');
    } else {
      res = await api.login(email, password);
      showToast(`Welcome back, ${res.user.full_name}!`, 'success');
    }

    api.setToken(res.access_token);
    state.currentUser = res.user;
    updateAuthUI();
    closeModal('auth-modal');
    loadUserDashboard();

  } catch (err) {
    showToast(err.message, 'error');
  }
};

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

function setupEventListeners() {
  // Navigation
  document.getElementById('nav-home-link')?.addEventListener('click', () => showView('home'));
  document.getElementById('nav-dashboard-link')?.addEventListener('click', () => {
    if (!state.currentUser) {
      showToast('Please login to view your dashboard.', 'info');
      openAuthModal();
    } else {
      loadUserDashboard();
      showView('dashboard');
    }
  });
  document.getElementById('nav-admin-link')?.addEventListener('click', () => loadAdminDashboard());
}
