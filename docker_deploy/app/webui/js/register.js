/**
 * Z-Ray  •  Registration Logic
 * ============================================
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registerForm');
  const btnRegister = document.getElementById('btnRegister');
  const btnText = btnRegister.querySelector('.btn-text');
  
  const alertBox = document.getElementById('errorMessage');
  const alertText = document.getElementById('errorText');

  function showError(msg) {
    alertBox.style.display = 'flex';
    alertText.textContent = msg;
    alertBox.classList.add('shake');
    setTimeout(() => alertBox.classList.remove('shake'), 500);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fullName = document.getElementById('fullName').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const address = document.getElementById('address').value.trim();
    const licenseNo = document.getElementById('licenseNo').value.trim();

    if (!fullName || !username || !password || !address || !licenseNo) {
      showError('Please fill in all requested fields.');
      return;
    }

    // Reset UI
    alertBox.style.display = 'none';
    btnRegister.classList.add('loading');
    btnRegister.disabled = true;

    try {
      const res = await fetch(`${ZRAY_API}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          full_name: fullName,
          username: username,
          password: password,
          address: address,
          license_no: licenseNo
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      // Success
      btnRegister.classList.remove('loading');
      btnText.textContent = 'Success! Redirecting...';
      btnRegister.style.backgroundColor = '#10b981'; // green
      btnRegister.style.borderColor = '#10b981';

      setTimeout(() => {
        window.location.href = 'index.html';
      }, 1500);

    } catch (err) {
      btnRegister.classList.remove('loading');
      btnRegister.disabled = false;
      showError(err.message);
    }
  });
});
