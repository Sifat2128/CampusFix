const card = (i, n) => `<button class="issue" data-id="${i.id}" style="--pc:var(--${i.status === 'closed' ? 'low' : i.priority});--i:${n}">
  <h3>${esc(i.title)}</h3><p>${esc(i.description)}</p>
  <div class="meta"><span class="chip s-${i.status}">${label(i.status)}</span>${i.status === 'closed' ? '' : `<span class="chip pr-${i.priority}">${i.priority}</span>`}<span class="chip">${i.category}</span>
  <span>by ${esc(i.user)}</span><span>assigned to ${esc(i.assigned_employee)}</span><span>${fmt(i.created_at)}</span></div></button>`;

function refresh() { loadStats(); loadList(); }

async function loadStats() {
  try {
    const res = await Promise.all(STAT.map(([k]) => api('/issues/?limit=1&status=' + k)));
    const tot = res.reduce((a, r) => a + r.total, 0);
    $('#stats').innerHTML = [['', 'All issues', tot], ...STAT.map(([k, l], i) => [k, l, res[i].total])]
      .map(([k, l, n]) => `<button class="stat${S.status === k ? ' on' : ''}" data-k="${k}"><b data-n="${n}">0</b><span>${l}</span></button>`).join('');
    document.querySelectorAll('.stat b').forEach(countUp);
    document.querySelectorAll('.stat').forEach(b => b.onclick = () => { S.status = b.dataset.k; S.skip = 0; loadStats(); loadList(); });
  } catch (e) { toast(e.message, 1); }
}

async function loadList() {
  const p = new URLSearchParams({ skip: S.skip, limit: S.limit });
  const q = $('#q').value.trim();
  if (q) p.set('search', q);
  if (S.status) p.set('status', S.status);
  if ($('#fPri').value) p.set('priority', $('#fPri').value);
  if ($('#fCat').value) p.set('category', $('#fCat').value);
  if (!$('#list').children.length) $('#list').innerHTML = '<div class="sk"></div>'.repeat(3);
  try {
    const r = await api('/issues/?' + p);
    r.data.forEach(i => S.cache[i.id] = i);
    $('#list').innerHTML = r.data.length ? r.data.map(card).join('')
      : `<div class="empty">No issues match these filters.${S.role === 'student' ? ' Use “Report an issue” to add one.' : ''}</div>`;
    document.querySelectorAll('.issue').forEach(c => c.onclick = () => openIssue(c.dataset.id));
    const end = Math.min(S.skip + S.limit, r.total);
    $('#pinfo').textContent = r.total ? `${S.skip + 1}–${end} of ${r.total}` : '0 results';
    $('#prev').disabled = S.skip === 0;
    $('#next').disabled = end >= r.total;
  } catch (e) { toast(e.message, 1); }
}

function initIssues() {
  $('#fPri').innerHTML += opts(PRIS);
  $('#fCat').innerHTML += opts(CATS);
  let t;
  $('#q').oninput = () => { clearTimeout(t); t = setTimeout(() => { S.skip = 0; loadList(); }, 300); };
  $('#fPri').onchange = $('#fCat').onchange = () => { S.skip = 0; loadList(); };
  $('#prev').onclick = () => { S.skip = Math.max(0, S.skip - S.limit); loadList(); };
  $('#next').onclick = () => { S.skip += S.limit; loadList(); };
  $('#newBtn').onclick = () => {
    layer(`<form class="modal" id="fNew"><h2 style="margin:0 0 4px">Report an issue</h2>
    <label>Title</label><input name="title" required>
    <label>Description</label><textarea name="description" required></textarea>
    <label>Category</label><select name="category">${opts(CATS)}</select>
    <label>Priority</label><select name="priority">${opts(PRIS, 'medium')}</select>
    <div class="row" style="justify-content:flex-end"><button type="button" class="btn" id="x">Cancel</button><button class="btn p">Submit issue</button></div></form>`, 1);
    $('#x').onclick = closeLayer;
    $('#fNew').onsubmit = guard(async e => {
      await api('/issues/create', { method: 'POST', json: Object.fromEntries(new FormData(e.target)) });
      closeLayer(); toast('Issue submitted'); refresh();
    });
  };
}
