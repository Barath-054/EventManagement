// Centralized REST API Client for EventMate AI
const API_BASE = window.location.origin;

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('eventmate_token') || null;
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('eventmate_token', token);
    } else {
      localStorage.removeItem('eventmate_token');
    }
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401) {
        this.setToken(null);
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'An error occurred during request.');
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // Auth
  login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  register(payload) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  getMe() {
    return this.request('/api/auth/me');
  }

  // Metadata
  getLocalities() {
    return this.request('/api/meta/localities');
  }

  getVenueTypes() {
    return this.request('/api/meta/venue-types');
  }

  getVendors() {
    return this.request('/api/meta/vendors');
  }

  // Categories & Services
  getCategories() {
    return this.request('/api/categories');
  }

  getPackages(categoryId = null, categoryCode = null) {
    let url = '/api/packages';
    if (categoryId) url += `?category_id=${categoryId}`;
    else if (categoryCode) url += `?category_code=${categoryCode}`;
    return this.request(url);
  }

  getServices(categoryCode = null) {
    const url = categoryCode ? `/api/services?category_code=${categoryCode}` : '/api/services';
    return this.request(url);
  }

  // AI Recommendation Engine
  analyzeEvent(payload) {
    return this.request('/api/recommendations/analyze', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Events
  createEvent(payload) {
    return this.request('/api/events', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  getEvents() {
    return this.request('/api/events');
  }

  getEvent(id) {
    return this.request(`/api/events/${id}`);
  }

  // Quotations & Pricing
  previewQuotation(payload) {
    return this.request('/api/quotations/preview', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  generateQuotation(payload) {
    return this.request('/api/quotations/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  getQuotation(id) {
    return this.request(`/api/quotations/${id}`);
  }

  approveQuotation(id) {
    return this.request(`/api/quotations/${id}/approve`, {
      method: 'POST'
    });
  }

  requestQuotationChange(id, payload) {
    return this.request(`/api/quotations/${id}/request-change`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Payments
  processAdvancePayment(payload) {
    return this.request('/api/payments/process-advance', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Bookings & Execution
  getBookingByEvent(eventId) {
    return this.request(`/api/bookings/event/${eventId}`);
  }

  updateTaskStatus(bookingId, taskId, status) {
    return this.request(`/api/bookings/${bookingId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
  }

  // Reviews
  submitReview(payload) {
    return this.request('/api/reviews', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  getReviews() {
    return this.request('/api/reviews');
  }

  // Admin Console
  getAdminMetrics() {
    return this.request('/api/admin/metrics');
  }

  getAdminEvents(filters = {}) {
    let query = new URLSearchParams(filters).toString();
    return this.request(`/api/admin/events?${query}`);
  }

  createCategory(payload) {
    return this.request('/api/categories', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  createService(payload) {
    return this.request('/api/services', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }
}

window.api = new ApiClient();
