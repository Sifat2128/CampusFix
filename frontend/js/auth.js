function show() {
  const a = !!S.token;
  $('#auth').classList.toggle('hide', a);
  $('#app').classList.toggle('hide', !a);
  const fab = $('#aiFab');
  if (fab) fab.classList.toggle('hide', !a);
  if (!a && typeof closeAiChat === 'function') closeAiChat();
  if (a) {
    $('#who').innerHTML = `${esc(S.email)} · <b>${esc(S.role)}</b>`;
    $('#av').textContent = S.email[0] || '?';
    $('#newBtn').classList.toggle('hide', S.role !== 'student');
    refresh();
  }
}
function logout() {
  ['cf_token', 'cf_role', 'cf_email'].forEach(k => localStorage.removeItem(k));
  S.token = ''; closeLayer();
  if (typeof closeAiChat === 'function') closeAiChat();
  show();
}
function authTab(login) {
  $('#fLogin').classList.toggle('hide', !login);
  $('#fReg').classList.toggle('hide', login);
  $('#tLogin').classList.toggle('on', login);
  $('#tReg').classList.toggle('on', !login);
}

function openForgotModal() {
  const prefill = $('#fLogin [name=email]')?.value || '';
  layer(`
    <div class="modal" style="max-width:440px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
        <div style="width:48px;height:48px;border-radius:14px;background:rgba(255,176,32,0.12);border:1px solid rgba(255,176,32,0.3);display:flex;align-items:center;justify-content:center;font-size:22px">🔐</div>
        <button type="button" class="btn" id="closeForgotModal" style="padding:6px 12px;font-size:13px">✕</button>
      </div>
      <h2 style="margin:0 0 6px;font-size:20px;font-weight:800">Reset your password</h2>
      <p style="color:var(--mute);font-size:13.5px;line-height:1.5;margin:0 0 18px">
        Enter your registered email address and we will send you a secure link to reset your password.
      </p>
      <form id="fForgot">
        <label style="display:block;margin-bottom:6px;font-weight:600;font-size:13px">Account Email</label>
        <input name="email" type="email" placeholder="name@campus.edu" required value="${esc(prefill)}" style="width:100%;margin-bottom:18px">
        <div class="row" style="margin:0;justify-content:flex-end;gap:10px">
          <button type="button" class="btn" id="cancelForgotBtn">Cancel</button>
          <button class="btn p" style="background:linear-gradient(120deg,#ff8008,#ffc837);border:none;color:#fff;font-weight:700">Send Reset Link</button>
        </div>
      </form>
    </div>
  `, 1);

  $('#closeForgotModal').onclick = closeLayer;
  $('#cancelForgotBtn').onclick = closeLayer;
  $('#fForgot').onsubmit = guard(async e => {
    const email = new FormData(e.target).get('email').trim();
    await api('/auth/forget?email=' + encodeURIComponent(email), { method: 'POST' });
    toast('Password reset email sent!');
    layer(`
      <div class="modal" style="text-align:center;max-width:440px">
        <div style="width:68px;height:68px;margin:0 auto 16px;border-radius:50%;background:rgba(34,211,238,0.15);border:1.5px solid rgba(34,211,238,0.3);display:flex;align-items:center;justify-content:center;font-size:32px">📬</div>
        <h2 style="margin:0 0 8px;font-size:20px;font-weight:800">Check Your Inbox</h2>
        <p style="color:var(--mute);font-size:14px;line-height:1.6;margin:0 0 22px">
          We sent a reset link to <strong style="color:var(--ink)">${esc(email)}</strong>.<br>Click the link in your email to choose a new password.
        </p>
        <button class="btn p" id="closeForgotSuccess" style="width:100%">Back to Login</button>
      </div>
    `, 1);
    $('#closeForgotSuccess').onclick = closeLayer;
  });
}

function openResendVerifModal() {
  const prefill = $('#fLogin [name=email]') ? $('#fLogin [name=email]').value.trim() : '';
  layer(`
    <div class="modal" style="max-width:440px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
        <div style="width:48px;height:48px;border-radius:14px;background:rgba(124,92,255,0.12);border:1px solid rgba(124,92,255,0.3);display:flex;align-items:center;justify-content:center;font-size:22px">✉️</div>
        <button type="button" class="btn" id="closeResendModal" style="padding:6px 12px;font-size:13px">✕</button>
      </div>
      <h2 style="margin:0 0 6px;font-size:20px;font-weight:800">Resend Activation Link</h2>
      <p style="color:var(--mute);font-size:13.5px;line-height:1.5;margin:0 0 18px">
        Didn't receive your verification email? Enter your email address and we will send a new activation link to your inbox.
      </p>
      <form id="fResend">
        <label style="display:block;margin-bottom:6px;font-weight:600;font-size:13px">Account Email</label>
        <input name="email" type="email" placeholder="e.g. 2203098@student.ruet.ac.bd" required value="${esc(prefill)}" style="width:100%;margin-bottom:18px">
        <div class="row" style="margin:0;justify-content:flex-end;gap:10px">
          <button type="button" class="btn" id="cancelResendBtn">Cancel</button>
          <button class="btn p" style="background:linear-gradient(120deg,#7c5cff,#9d80ff);border:none;color:#fff;font-weight:700">Send Link</button>
        </div>
      </form>
    </div>
  `, 1);

  $('#closeResendModal').onclick = closeLayer;
  $('#cancelResendBtn').onclick = closeLayer;
  $('#fResend').onsubmit = guard(async e => {
    const email = new FormData(e.target).get('email').trim();
    const res = await api('/auth/resend-verification?email=' + encodeURIComponent(email), { method: 'POST' });
    toast(res.message || 'Verification link sent!');
    layer(`
      <div class="modal" style="text-align:center;max-width:440px">
        <div style="width:68px;height:68px;margin:0 auto 16px;border-radius:50%;background:rgba(124,92,255,0.15);border:1.5px solid rgba(124,92,255,0.3);display:flex;align-items:center;justify-content:center;font-size:32px">📬</div>
        <h2 style="margin:0 0 8px;font-size:20px;font-weight:800">Check Your Inbox</h2>
        <p style="color:var(--mute);font-size:14px;line-height:1.6;margin:0 0 22px">
          We sent a new activation link to <strong style="color:var(--ink)">${esc(email)}</strong>.<br>Please check your inbox or spam folder.
        </p>
        <button class="btn p" id="closeResendSuccess" style="width:100%">Got It</button>
      </div>
    `, 1);
    $('#closeResendSuccess').onclick = closeLayer;
  });
}

function checkResetToken() {
  const params = new URLSearchParams(location.search);
  const token = params.get('reset_token') || params.get('token');
  if (!token) return;

  layer(`
    <div class="modal" style="max-width:440px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
        <div style="width:48px;height:48px;border-radius:14px;background:rgba(124,92,255,0.15);border:1px solid rgba(124,92,255,0.3);display:flex;align-items:center;justify-content:center;font-size:22px">🔑</div>
        <button type="button" class="btn" id="closeResetModal" style="padding:6px 12px;font-size:13px">✕</button>
      </div>
      <h2 style="margin:0 0 6px;font-size:20px;font-weight:800">Set New Password</h2>
      <p style="color:var(--mute);font-size:13.5px;line-height:1.5;margin:0 0 18px">
        Enter your new password below (minimum 6 characters).
      </p>
      <form id="fResetPass">
        <label style="display:block;margin-bottom:6px;font-weight:600;font-size:13px">New Password</label>
        <input name="password" type="password" required minlength="6" maxlength="72" placeholder="Minimum 6 characters" autocomplete="new-password" style="width:100%;margin-bottom:14px">
        <label style="display:block;margin-bottom:6px;font-weight:600;font-size:13px">Confirm New Password</label>
        <input name="confirm_password" type="password" required minlength="6" maxlength="72" placeholder="Re-enter your password" autocomplete="new-password" style="width:100%;margin-bottom:20px">
        <div class="row" style="margin:0;justify-content:flex-end">
          <button class="btn p" style="width:100%;font-weight:700">Update Password & Log In</button>
        </div>
      </form>
    </div>
  `, 1);

  $('#closeResetModal').onclick = () => {
    history.replaceState({}, '', location.pathname);
    closeLayer();
  };

  $('#fResetPass').onsubmit = guard(async e => {
    const fd = new FormData(e.target);
    const pass = fd.get('password');
    const confirm = fd.get('confirm_password');
    if (pass !== confirm) {
      toast('Passwords do not match', 1);
      return;
    }
    const updated = await api('/auth/reset-password?token=' + encodeURIComponent(token), {
      method: 'POST',
      json: { password: pass }
    });
    history.replaceState({}, '', location.pathname);
    closeLayer();
    confetti(50);
    toast('Password changed! You can now log in.');
    authTab(true);
    if (updated?.email) {
      const em = $('#fLogin [name=email]');
      if (em) em.value = updated.email;
      const pw = $('#fLogin [name=password]');
      if (pw) {
        pw.value = pass;
        pw.focus();
      }
    }
  });
}

function validateRuetEmail(email, role) {
  const e = (email || '').toLowerCase().trim();
  if (role === 'student') {
    if (!e.includes('student') || !e.includes('ruet')) {
      return "RUET students must use an email containing both 'student' and 'ruet' (e.g. 2203098@student.ruet.ac.bd).";
    }
  } else if (role === 'faculty') {
    if (!e.includes('ruet')) {
      return "Teachers/Faculty must use their official RUET email containing 'ruet' (e.g. teacher@dept.ruet.ac.bd).";
    }
  } else if (role === 'staff') {
    if (!e.includes('ruet')) {
      return "Staff members must use their official RUET email containing 'ruet' (e.g. staff@ruet.ac.bd).";
    }
  }
  return null;
}

function updateRoleGuide(formType) {
  const isReg = formType === 'reg';
  const roleSelect = $(isReg ? '#regRole' : '#loginRole');
  const emailInput = $(isReg ? '#regEmail' : '#loginEmail');
  const guideBox = $('#emailGuideBox');
  if (!roleSelect || !emailInput) return;

  const role = roleSelect.value;
  if (role === 'student') {
    emailInput.placeholder = 'e.g. 2203098@student.ruet.ac.bd';
    if (guideBox && isReg) {
      guideBox.innerHTML = '🎓 <strong>RUET Students:</strong> Email must contain <code>student</code> and <code>ruet</code> (e.g., <em>2203098@student.ruet.ac.bd</em>)';
    }
  } else if (role === 'faculty') {
    emailInput.placeholder = 'e.g. teacher@dept.ruet.ac.bd';
    if (guideBox && isReg) {
      guideBox.innerHTML = '👨‍🏫 <strong>Teachers/Faculty:</strong> Email must contain <code>ruet</code> (e.g., <em>teacher@dept.ruet.ac.bd</em>)';
    }
  } else if (role === 'staff') {
    emailInput.placeholder = 'e.g. staff@ruet.ac.bd';
    if (guideBox && isReg) {
      guideBox.innerHTML = '🛠️ <strong>RUET Staff:</strong> Email must contain <code>ruet</code> (e.g., <em>staff@ruet.ac.bd</em>)';
    }
  } else if (role === 'admin') {
    emailInput.placeholder = 'e.g. admin@...';
    if (guideBox && isReg) {
      guideBox.innerHTML = '🛡️ <strong>Admin Portal:</strong> Use your designated administrator email credentials.';
    }
  }
}

function initAuth() {
  $('#tLogin').onclick = () => { authTab(true); updateRoleGuide('login'); };
  $('#tReg').onclick = () => { authTab(false); updateRoleGuide('reg'); };
  const forgotBtn = $('#btnForgot');
  if (forgotBtn) forgotBtn.onclick = openForgotModal;
  const resendBtn = $('#btnResendVerif');
  if (resendBtn) resendBtn.onclick = openResendVerifModal;
  checkResetToken();

  const regRole = $('#regRole');
  if (regRole) regRole.onchange = () => updateRoleGuide('reg');
  const loginRole = $('#loginRole');
  if (loginRole) loginRole.onchange = () => updateRoleGuide('login');
  updateRoleGuide('login');

  $('#fLogin').onsubmit = guard(async e => {
    const f = Object.fromEntries(new FormData(e.target));
    const valErr = validateRuetEmail(f.email, f.role);
    if (valErr) {
      toast(valErr, 'error');
      return;
    }
    const r = await api('/auth/login', { method: 'POST', json: { email: f.email, password: f.password, role: f.role } });
    const known = JSON.parse(localStorage.cf_roles || '{}')[f.email];
    S.token = r.access_token; S.email = f.email; S.role = known || f.role;
    localStorage.cf_token = S.token; localStorage.cf_email = S.email; localStorage.cf_role = S.role;
    show();
  });
  $('#fReg').onsubmit = guard(async e => {
    const f = Object.fromEntries(new FormData(e.target));
    const valErr = validateRuetEmail(f.email, f.role);
    if (valErr) {
      toast(valErr, 'error');
      return;
    }
    await api('/auth/register', { method: 'POST', json: f });
    const m = JSON.parse(localStorage.cf_roles || '{}'); m[f.email] = f.role;
    localStorage.cf_roles = JSON.stringify(m);
    toast('Account created! Please check your email.');
    layer(`<div class="modal" style="text-align:center;max-width:440px">
      <div style="width:68px;height:68px;margin:0 auto 16px;border-radius:50%;background:rgba(124,92,255,0.15);border:1.5px solid rgba(124,92,255,0.3);display:flex;align-items:center;justify-content:center;font-size:32px">✉️</div>
      <h2 style="margin:0 0 8px">Verify Your Email</h2>
      <p style="color:var(--mute);font-size:14px;line-height:1.6;margin:0 0 20px">We've sent a magic verification link to <strong style="color:var(--ink)">${esc(f.email)}</strong>. Click the link in your inbox to activate your account.</p>
      <button class="btn p" id="closeRegModal" style="width:100%">Got it, back to login</button>
    </div>`, 1);
    $('#closeRegModal').onclick = closeLayer;
    confetti(40);
    e.target.reset(); authTab(true); $('#fLogin [name=email]').value = f.email;
  });
  $('#out').onclick = logout;
  $('#theme').onclick = () => {
    const d = document.documentElement;
    const dark = (d.dataset.theme || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light')) === 'dark';
    d.dataset.theme = dark ? 'light' : 'dark';
  };
}
