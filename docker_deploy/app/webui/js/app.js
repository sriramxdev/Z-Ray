/* ============================================
   Z-Ray  •  Login Logic (API-backed)
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('loginForm');
  const usernameIn = document.getElementById('username');
  const passwordIn = document.getElementById('password');
  const errorBox   = document.getElementById('errorMessage');
  const errorText  = document.getElementById('errorText');
  const btnLogin   = document.getElementById('btnLogin');
  const togglePwd  = document.getElementById('togglePassword');

  /* ---------- Password visibility toggle ---------- */
  if (togglePwd) {
    togglePwd.addEventListener('click', () => {
      const isPassword = passwordIn.type === 'password';
      passwordIn.type  = isPassword ? 'text' : 'password';
      togglePwd.innerHTML = isPassword
        ? '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>'
        : '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>';
      togglePwd.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
    });
  }

  /* ---------- Show / Hide error ---------- */
  function showError(msg) {
    errorText.textContent = msg;
    errorBox.classList.add('visible');
    errorBox.style.animation = 'none';
    void errorBox.offsetWidth;
    errorBox.style.animation = '';
  }

  function hideError() {
    errorBox.classList.remove('visible');
  }

  /* ---------- Form submit — API call ---------- */
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const user = usernameIn.value.trim();
    const pass = passwordIn.value;

    if (!user || !pass) {
      showError('Please enter both username and password.');
      if (!user) usernameIn.classList.add('input-error');
      if (!pass) passwordIn.classList.add('input-error');
      return;
    }

    usernameIn.classList.remove('input-error');
    passwordIn.classList.remove('input-error');

    btnLogin.classList.add('loading');
    btnLogin.disabled = true;

    try {
      const res = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pass })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Login failed');
      }

      /* Store auth data */
      sessionStorage.setItem('zray_token', data.token);
      sessionStorage.setItem('zray_user', data.username);
      sessionStorage.setItem('zray_fullname', data.full_name || data.username);

      /* Redirect to dashboard */
      window.location.href = 'dashboard.html';

    } catch (err) {
      btnLogin.classList.remove('loading');
      btnLogin.disabled = false;
      showError(err.message || 'Invalid username or password. Please try again.');
      passwordIn.value = '';
      passwordIn.focus();
    }
  });

  /* Remove per-field error style on input */
  [usernameIn, passwordIn].forEach(input => {
    input.addEventListener('input', () => {
      input.classList.remove('input-error');
      hideError();
    });
  });
});
