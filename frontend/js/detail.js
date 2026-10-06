async function openIssue(id) {
  try {
    let i;
    try { i = await api('/issues/' + id); }
    catch (e) {
      // Backend only lets owner/assignee/admin open an issue; others get a read-only view from the list.
      if (e.status === 403 && S.cache[id]) i = { ...S.cache[id], _ro: true }; else throw e;
    }
    const student = S.role === 'student';
    const [cm, hist, vote] = await Promise.all([
      api(`/issues/${id}/comments`).catch(() => []),
      api(`/issues/${id}/history`).catch(() => null),   // backend decides who may see it
      student ? api(`/issues/${id}/vote`).catch(() => null) : null   // null/500 = not voted yet
    ]);
    renderDetail(i, cm, hist, vote);
  } catch (e) { toast(e.message, 1); }
}

function renderDetail(i, cm, hist, vote) {
  const idx = STAT.findIndex(s => s[0] === i.status), r = S.role, acts = [];
  if (!i._ro) {
    if (r === 'staff' && i.status === 'open') acts.push(['start', 'Start work', 'p']);
    if (r === 'staff' && i.status === 'in_progress') acts.push(['resolve', 'Mark resolved', 'p']);
    if (r === 'student' && i.status === 'resolved') acts.push(['close', 'Confirm and close', 'p']);
    if ((r === 'student' && i.status === 'open') || r === 'admin') acts.push(['edit', 'Edit', '']);
  }
  const tl = hist && hist.length
    ? `<h3>History</h3><ol class="tl">${[...hist].sort((a, b) => a.id - b.id).map(h => `<li>${esc(h.action)}<small>${fmt(h.time)}</small></li>`).join('')}</ol>` : '';
  const commentForm = i._ro
    ? `<p class="mute">This issue belongs to someone else, so you can read it but not comment.</p>`
    : `<form id="fc" style="margin-top:12px"><textarea name="content" placeholder="Write a comment" required style="min-height:70px"></textarea><div class="row"><button class="btn p">Post comment</button></div></form>`;
  const d = layer(`<aside class="drawer">
   <div style="display:flex;justify-content:space-between;gap:8px"><span class="chip s-${i.status}">${label(i.status)}</span><button class="btn" id="x">Close</button></div>
   <h2 style="margin:10px 0 4px">${esc(i.title)}</h2>
   <div class="pipe">${STAT.map(([k, l], n) => `<div style="--n:${n}" class="${n <= idx ? 'done' : ''}">${l}</div>`).join('')}</div>
   <p style="white-space:pre-wrap">${esc(i.description)}</p>
   <dl class="kv">${i.status === 'closed' ? '' : `<dt>Priority</dt><dd>${i.priority}</dd>`}<dt>Category</dt><dd>${i.category}</dd><dt>Reported by</dt><dd>${esc(i.user)}</dd><dt>Assigned to</dt><dd>${esc(i.assigned_employee)}</dd><dt>Created</dt><dd style="text-transform:none">${fmt(i.created_at)}</dd></dl>
   ${r === 'student' ? `<div class="row"><button class="btn" id="vote"></button><span class="mute" id="vc"></span></div>` : ''}
   <div class="row">${acts.map(([k, l, c]) => `<button class="btn ${c}" data-a="${k}">${l}</button>`).join('')}</div>
   <div id="editbox"></div>
   ${tl}
   <h3>Comments (${cm.length})</h3>
   ${cm.map(c => `<div class="cm"><b>${esc(c.user_info?.name)}</b> <small>${c.user_info?.role} · ${fmt(c.created_at)}</small><div style="white-space:pre-wrap">${esc(c.content)}</div></div>`).join('') || '<p class="mute">No comments yet.</p>'}
   ${commentForm}
  </aside>`);
  $('#x').onclick = closeLayer;

  if (r === 'student') {
    let voted = vote ? (vote.voted ?? true) : false, total = vote ? vote.total_votes : null;
    const paint = () => {
      $('#vote').className = 'btn' + (voted ? ' p' : '');
      $('#vote').textContent = voted ? '✓ Same problem here' : 'Same problem here';
      $('#vc').textContent = total == null ? '' : `${total} ${total === 1 ? 'student has' : 'students have'} this problem`;
    };
    paint();
    $('#vote').onclick = guard(async () => {
      const res = await api(`/issues/${i.id}/vote`, { method: 'POST', json: { like: 1 } }); // endpoint toggles
      voted = res.voted ?? !voted; total = res.total_votes; paint(); if (voted) confetti(30);
    });
  }

  d.querySelectorAll('[data-a]').forEach(b => b.onclick = guard(async () => {
    const a = b.dataset.a;
    if (a === 'edit') return editForm(i);
    await api(`/issues/${i.id}/${a}`, { method: 'POST' });
    if (a !== 'start') confetti();
    toast({ start: 'Work started', resolve: 'Issue resolved', close: 'Issue closed' }[a]);
    refresh(); openIssue(i.id);
  }));
  if ($('#fc')) $('#fc').onsubmit = guard(async e => {
    await api(`/issues/${i.id}/comments`, { method: 'POST', json: { content: new FormData(e.target).get('content') } });
    toast('Comment posted'); openIssue(i.id);
  });
}

function editForm(i) {
  $('#editbox').innerHTML = `<form id="fe" class="cm"><label style="margin-top:0">Title</label><input name="title" value="${esc(i.title)}" required>
  <label>Description</label><textarea name="description" required>${esc(i.description)}</textarea>
  <label>Category</label><select name="category">${opts(CATS, i.category)}</select><label>Priority</label><select name="priority">${opts(PRIS, i.priority)}</select>
  <div class="row"><button class="btn p">Save changes</button></div></form>`;
  $('#fe').onsubmit = guard(async e => {
    await api('/issues/' + i.id, { method: 'PATCH', json: Object.fromEntries(new FormData(e.target)) });
    toast('Changes saved'); refresh(); openIssue(i.id);
  });
}
