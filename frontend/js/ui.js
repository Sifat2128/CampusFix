const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const label = s => String(s).replace('_', ' ');
const fmt = d => new Date(/Z|[+-]\d\d:?\d\d$/.test(d) ? d : d + 'Z').toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
const opts = (arr, sel) => arr.map(v => `<option value="${v}"${v === sel ? ' selected' : ''}>${label(v)}</option>`).join('');

function toast(m, err) {
  const t = document.createElement('div');
  t.className = 'toast' + (err ? ' err' : '');
  t.textContent = m;
  $('#toasts').append(t);
  setTimeout(() => t.remove(), 3500);
}
function closeLayer() { $('#layer').innerHTML = ''; }
function layer(html, mid) {
  const l = $('#layer');
  l.innerHTML = `<div class="scrim${mid ? ' mid' : ''}">${html}</div>`;
  const s = l.firstChild;
  s.onclick = e => { if (e.target === s) closeLayer(); };
  return s;
}
// Wraps a handler: prevents default, disables the button, shows errors as toasts.
const guard = fn => async e => {
  e?.preventDefault?.();
  const b = e?.submitter || e?.target;
  if (b) b.disabled = true;
  try { await fn(e); } catch (x) { toast(x.message, 1); } finally { if (b) b.disabled = false; }
};

const CONF = ['#7c5cff', '#22d3ee', '#a3e635', '#fb7185', '#fbbf24'];
function confetti(n = 70) {
  for (let k = 0; k < n; k++) {
    const p = document.createElement('i'); p.className = 'cf';
    p.style.cssText = `left:50%;top:40%;background:${CONF[k % 5]};--x:${(Math.random() - .5) * 900}px;--y:${-Math.random() * 500 - 100}px;--r:${Math.random() * 720}deg`;
    document.body.append(p); setTimeout(() => p.remove(), 1400);
  }
}
function countUp(el) {
  const to = +el.dataset.n; let t0;
  const f = t => { t0 ??= t; const k = Math.min((t - t0) / 700, 1); el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(f); };
  requestAnimationFrame(f);
}
