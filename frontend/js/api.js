async function api(path, { method = 'GET', json, form } = {}) {
  const h = {};
  if (S.token) h.Authorization = 'Bearer ' + S.token;
  let body;
  if (json) { h['Content-Type'] = 'application/json'; body = JSON.stringify(json); }
  if (form) body = new URLSearchParams(form);
  let r;
  try { r = await fetch(API + path, { method, headers: h, body }); }
  catch { throw new Error('Cannot reach the server. Is the backend running?'); }
  if (r.status === 401 && S.token) { logout(); throw new Error('Session expired. Please log in again.'); }
  const data = await r.json().catch(() => null);
  if (!r.ok) {
    const d = data?.detail;
    const err = new Error(typeof d === 'string' ? d
      : Array.isArray(d) ? d.map(e => e.loc.slice(1).join('.') + ': ' + e.msg).join('; ')
        : 'Request failed (' + r.status + ')');
    err.status = r.status;
    throw err;
  }
  return data;
}
