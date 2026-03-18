/* ============================================
   Z-Ray  •  Auth Helper (shared across pages)
   ============================================ */

const ZRAY_API = 'http://localhost:5000';

/** Get the stored JWT token */
function getToken() {
  return sessionStorage.getItem('zray_token');
}

/** Get the stored username */
function getUser() {
  return sessionStorage.getItem('zray_user');
}

/** Check if user is authenticated, redirect to login if not */
function requireAuth() {
  if (!getToken()) {
    window.location.href = 'index.html';
    return false;
  }
  return true;
}

/** Set up header user display and logout button */
function setupHeader() {
  const userEl = document.getElementById('headerUser');
  const logoutBtn = document.getElementById('btnLogout');

  if (userEl) userEl.textContent = getUser() || '';

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      sessionStorage.removeItem('zray_token');
      sessionStorage.removeItem('zray_user');
      sessionStorage.removeItem('zray_fullname');
      window.location.href = 'index.html';
    });
  }
}

/** Make an authenticated API request */
async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const res = await fetch(`${ZRAY_API}${endpoint}`, {
    ...options,
    headers
  });

  const data = await res.json();

  if (!res.ok) {
    if (res.status === 401) {
      sessionStorage.clear();
      window.location.href = 'index.html';
    }
    throw new Error(data.error || 'Request failed');
  }

  return data;
}
