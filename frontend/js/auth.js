function show() {
  const a = !!S.token;
  $('#auth').classList.toggle('hide', a);
  $('#app').classList.toggle('hide', !a);
  if (a) {
    $('#who').innerHTML = `${esc(S.email)} · <b>${esc(S.role)}</b>`;
    $('#av').textContent = S.email[0] || '?';
    $('#newBtn').classList.toggle('hide', S.role !== 'student');
    refresh();
  }
}
function logout() {
  ['cf_token','cf_role','cf_email'].forEach(k => localStorage.removeItem(k));
  S.token = ''; closeLayer(); show();
}
function authTab(login) {
  $('#fLogin').classList.toggle('hide', !login);
  $('#fReg').classList.toggle('hide', login);
  $('#tLogin').classList.toggle('on', login);
  $('#tReg').classList.toggle('on', !login);
}
function initAuth() {
  $('#tLogin').onclick = () => authTab(true);
  $('#tReg').onclick = () => authTab(false);
  $('#fLogin').onsubmit = guard(async e => {
    const f = Object.fromEntries(new FormData(e.target));
    const r = await api('/auth/login', { method: 'POST', form: { username: f.email, password: f.password } });
    const known = JSON.parse(localStorage.cf_roles || '{}')[f.email];
    S.token = r.access_token; S.email = f.email; S.role = known || f.role;
    localStorage.cf_token = S.token; localStorage.cf_email = S.email; localStorage.cf_role = S.role;
    show();
  });
  $('#fReg').onsubmit = guard(async e => {
    const f = Object.fromEntries(new FormData(e.target));
    await api('/auth/register', { method: 'POST', json: f });
    const m = JSON.parse(localStorage.cf_roles || '{}'); m[f.email] = f.role;
    localStorage.cf_roles = JSON.stringify(m);
    toast('Account created. Log in to continue.');
    e.target.reset(); authTab(true); $('#fLogin [name=email]').value = f.email;
  });
  $('#out').onclick = logout;
  $('#theme').onclick = () => {
    const d = document.documentElement;
    const dark = (d.dataset.theme || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light')) === 'dark';
    d.dataset.theme = dark ? 'light' : 'dark';
  };
}
