"""Part 2: staff lifecycle, role-modal recovery, admin/faculty restrictions."""
import json, subprocess, time, urllib.request, os, sys
import websocket, requests, uuid

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9334
BASE = "http://127.0.0.1:8000"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_chrome_profile2")

proc = subprocess.Popen([
    CHROME, "--headless=new", f"--remote-debugging-port={PORT}", "--disable-gpu",
    "--no-first-run", "--no-default-browser-check", "--window-size=1400,1000",
    f"--user-data-dir={OUT}", "--remote-allow-origins=*", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for _ in range(60):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1).read(); break
    except Exception: time.sleep(0.5)

req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?{BASE}/ui/", method="PUT")
target = json.loads(urllib.request.urlopen(req, timeout=10).read())
ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=30, suppress_origin=True)
_id = [0]
def send(method, **p):
    _id[0] += 1
    ws.send(json.dumps({"id": _id[0], "method": method, "params": p}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == _id[0]: return m.get("result", {})
def ev(e):
    r = send("Runtime.evaluate", expression=e, returnByValue=True, userGesture=True)
    if "exceptionDetails" in r:
        return {"__error__": (r["exceptionDetails"].get("exception") or {}).get("description")}
    return r.get("result", {}).get("value")
errors = []
def drain(s=1.5):
    end = time.time() + s
    ws.settimeout(0.4)
    while time.time() < end:
        try:
            m = json.loads(ws.recv())
            if m.get("method") == "Runtime.exceptionThrown":
                d = m["params"]["exceptionDetails"]
                errors.append(d.get("exception", {}).get("description") or d.get("text"))
        except Exception: pass
    ws.settimeout(30)

send("Runtime.enable"); send("Page.enable"); drain(2.5)
ev("localStorage.clear()"); send("Page.reload"); drain(3.0)

fails = []
def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label:50} got={got!r}" + ("" if ok else f"  want={want!r}"))
    if not ok: fails.append(label)

def login(email, pw="password123"):
    ev("Array.from(document.querySelectorAll('.toast')).forEach(t=>t.remove())")
    ev(f"""(()=>{{
      document.getElementById('tabLogin').click();
      document.getElementById('loginEmail').value='{email}';
      document.getElementById('loginPassword').value='{pw}';
      document.getElementById('loginForm').requestSubmit();
    }})()""")
    drain(2.5)

def pick_modal_role(role, name=None):
    ev(f"""(()=>{{
      if(document.getElementById('roleModal').open){{
        const n=document.getElementById('profileName');
        n.value={json.dumps(name) if name else ''};
        document.querySelectorAll('#rolePick .role').forEach(b=>{{if(b.dataset.role==='{role}')b.click();}});
        document.getElementById('roleConfirm').click();
      }}
    }})()""")
    drain(2.0)

def open_issue(iid):
    ev(f"""(()=>{{const i=document.getElementById('lookupId');i.value='{iid}';
      document.getElementById('lookupForm').requestSubmit();}})()""")
    drain(2.5)

print("=" * 78); print("M. fresh login, role unknown -> role modal must appear"); print("=" * 78)
ev("localStorage.clear()"); send("Page.reload"); drain(3.0)
email = f"staff{uuid.uuid4().hex[:6]}@t.com"
r = requests.post(f"{BASE}/auth/register", json={"name": "Fixer", "email": email,
                                                 "password": "password123", "role": "staff"})
assert r.status_code == 200, r.text
login(email)
check("role modal is open", ev("document.getElementById('roleModal').open"), True)
check("not logged in yet", ev("!document.getElementById('dashView').hidden"), False)
pick_modal_role("staff", "Fixer")
check("logged in after picking role", ev("!document.getElementById('dashView').hidden"), True)
check("role applied", ev("document.getElementById('userRole').textContent"), "staff")
check("role remembered", ev(f"JSON.parse(localStorage.getItem('cf_roles'))['{email}'].role"), "staff")
check("name remembered", ev(f"JSON.parse(localStorage.getItem('cf_roles'))['{email}'].name"), "Fixer")
check("sidebar title for staff", ev("document.getElementById('listTitle').textContent"), "Issues assigned to me")
check("staff cannot Report Issue", ev("document.getElementById('newIssueBtn').hidden"), True)

print(); print("=" * 78); print("N. staff lifecycle: open -> start -> resolve"); print("=" * 78)
su = f"own{uuid.uuid4().hex[:6]}@t.com"
requests.post(f"{BASE}/auth/register", json={"name": "Owner", "email": su, "password": "password123", "role": "student"})
stu = requests.post(f"{BASE}/auth/login", data={"username": su, "password": "password123"}).json()["access_token"]
created = requests.post(f"{BASE}/issues/create", json={"title": "lifecycle", "description": "d",
                         "category": "water", "priority": "medium"}, headers={"Authorization": f"Bearer {stu}"}).json()
iid = created["id"]
print(f"  issue #{iid} created, assigned to {created['assigned_employee']!r}")

# the auto-assigned staff is whoever has fewest jobs; find them by logging in as 'Fixer' if so
login(email)
pick_modal_role("staff", "Fixer")
open_issue(iid)
check("staff sees the issue", ev("document.getElementById('dTitle').textContent"), "lifecycle")
check("assigned staff may Start", ev("document.getElementById('startBtn').disabled"), False)
check("assigned staff may Resolve", ev("document.getElementById('resolveBtn').disabled"), False)
check("staff may NOT Close", ev("document.getElementById('closeBtn').disabled"), True)
check("staff may NOT Edit", ev("document.getElementById('editBtn').disabled"), True)

ev("document.getElementById('startBtn').click()"); drain(2.5)
check("status after Start", ev("document.getElementById('dStatus').textContent"), "in progress")
check("flow after start", ev("Array.from(document.querySelectorAll('.step')).map(s=>s.dataset.s+':'+(s.classList.contains('done')?'y':'n')).join(' ')"), "open:y in_progress:y resolved:n closed:n")
check("Start now disabled", ev("document.getElementById('startBtn').disabled"), True)
check("Resolve still enabled", ev("document.getElementById('resolveBtn').disabled"), False)

ev("document.getElementById('resolveBtn').click()"); drain(2.5)
check("status after Resolve", ev("document.getElementById('dStatus').textContent"), "resolved")
check("Resolve now disabled", ev("document.getElementById('resolveBtn').disabled"), True)
check("both staff buttons now disabled", ev("document.getElementById('startBtn').disabled && document.getElementById('resolveBtn').disabled"), True)

print(); print("=" * 78); print("O. staff cannot resolve twice (server rejects)"); print("=" * 78)
ev("document.getElementById('resolveBtn').click()"); drain(2.0)
check("button stayed disabled (no double fire)", ev("document.getElementById('resolveBtn').disabled"), True)

print(); print("=" * 78); print("P. student closes the resolved issue"); print("=" * 78)
login(su); pick_modal_role("student", "Owner")
open_issue(iid)
check("student sees it", ev("document.getElementById('dStatus').textContent"), "resolved")
check("owner may Close", ev("document.getElementById('closeBtn').disabled"), False)
check("owner may NOT Edit(resolved)", ev("document.getElementById('editBtn').disabled"), True)
ev("document.getElementById('closeBtn').click()"); drain(2.5)
check("status after Close", ev("document.getElementById('dStatus').textContent"), "closed")
check("all flow steps done", ev("Array.from(document.querySelectorAll('.step')).every(s=>s.classList.contains('done'))"), True)
check("all action buttons disabled when closed", ev(
    "['startBtn','resolveBtn','closeBtn'].every(id=>document.getElementById(id).disabled)"), True)

print(); print("=" * 78); print("Q. admin on someone else's issue: can edit, cannot comment"); print("=" * 78)
ae = f"adm{uuid.uuid4().hex[:6]}@t.com"
requests.post(f"{BASE}/auth/register", json={"name": "Boss", "email": ae, "password": "password123", "role": "admin"})
login(ae); pick_modal_role("admin", "Boss")
open_issue(iid)
check("admin can read any issue", ev("document.getElementById('dTitle').textContent"), "lifecycle")
check("admin may Edit", ev("document.getElementById('editBtn').disabled"), False)
check("admin comment box hidden", ev("document.getElementById('commentForm').hidden"), True)
check("admin sees the restriction note", ev("!document.getElementById('commentNote').hidden"), True)
check("admin may NOT Start", ev("document.getElementById('startBtn').disabled"), True)
check("admin may NOT Close", ev("document.getElementById('closeBtn').disabled"), True)

print(); print("=" * 78); print("R. faculty cannot comment anywhere"); print("=" * 78)
fe = f"fac{uuid.uuid4().hex[:6]}@t.com"
requests.post(f"{BASE}/auth/register", json={"name": "Prof", "email": fe, "password": "password123", "role": "faculty"})
login(fe); pick_modal_role("faculty", "Prof")
open_issue(iid)
check("faculty can read", ev("document.getElementById('dTitle').textContent"), "lifecycle")
check("faculty comment box hidden", ev("document.getElementById('commentForm').hidden"), True)
check("faculty note mentions faculty", ev("document.getElementById('commentNote').textContent"),
      "Faculty accounts cannot comment on this API.")

print(); print("=" * 78); print("S. edit an open issue end-to-end"); print("=" * 78)
newi = requests.post(f"{BASE}/issues/create", json={"title": "to edit", "description": "before",
                      "category": "other", "priority": "low"}, headers={"Authorization": f"Bearer {stu}"}).json()
nid = newi["id"]
login(su); pick_modal_role("student", "Owner")
open_issue(nid)
check("owner may edit open issue", ev("document.getElementById('editBtn').disabled"), False)
ev("document.getElementById('editBtn').click()"); drain(0.8)
check("modal prefilled with current title", ev("document.getElementById('fTitle').value"), "to edit")
check("modal prefilled priority", ev("document.getElementById('fPriority').value"), "low")
ev("document.getElementById('fTitle').value='edited title';"
   "document.getElementById('fPriority').value='high';"
   "document.getElementById('issueForm').requestSubmit();"); drain(3.0)
check("title updated in detail", ev("document.getElementById('dTitle').textContent"), "edited title")
check("priority updated", ev("document.getElementById('dPriority').textContent"), "⚑ High")
check("sidebar reflects new title", ev("Array.from(document.querySelectorAll('#issueList li .t')).some(e=>e.textContent.includes('edited title'))"), True)

print(); print("=" * 78); print("T. empty-title submit is blocked client-side"); print("=" * 78)
ev("document.getElementById('newIssueBtn') && document.getElementById('newIssueBtn').click()"); drain(0.5)
ev("document.getElementById('fTitle').value='   ';document.getElementById('fDesc').value='x';"
   "document.getElementById('issueForm').requestSubmit();"); drain(1.5)
check("modal stays open", ev("document.getElementById('issueModal').open"), True)
check("warned instead of sending", ev("Array.from(document.querySelectorAll('.toast')).some(t=>t.textContent.includes('Title and description'))"), True)
ev("document.getElementById('cancelModal').click()"); drain(0.5)

print(); print("=" * 78); print("U. bad lookup id"); print("=" * 78)
ev("Array.from(document.querySelectorAll('.toast')).forEach(t=>t.remove())")
ev("""(()=>{const i=document.getElementById('lookupId');i.value='abc';
  i.setAttribute('type','text');document.getElementById('lookupForm').requestSubmit();})()""")
drain(1.5)
ev("""(()=>{const i=document.getElementById('lookupId');i.value='-5';
  document.getElementById('lookupForm').requestSubmit();})()""")
drain(1.5)
check("rejects non-positive id", ev("Array.from(document.querySelectorAll('.toast')).some(t=>t.textContent.includes('valid issue number'))"), True)

print(); print("=" * 78); print("V. health check button"); print("=" * 78)
ev("Array.from(document.querySelectorAll('.toast')).forEach(t=>t.remove())")
ev("document.getElementById('runAllBtn').click()"); drain(3.5)
check("health toast shown", ev("Array.from(document.querySelectorAll('.toast')).some(t=>/reachable/.test(t.textContent))"), True)
ev("document.getElementById('clearLogBtn').click()"); drain(0.4)
check("log cleared", ev("document.getElementById('logList').children.length"), 0)

print(); print("=" * 78); print("W. shortcuts"); print("=" * 78)
ev("document.getElementById('logoutBtn').click()"); drain(0.8)
ev("""(()=>{const e=new KeyboardEvent('keydown',{key:'/',bubbles:true});
  document.body.dispatchEvent(e);})()""")
drain(0.6)
check("'/' ignored while logged out", ev("document.activeElement.id"), "")
login(su); pick_modal_role("student", "Owner")
ev("document.activeElement && document.activeElement.blur && document.activeElement.blur()")
drain(0.5)
print("   [focus before shortcut tests: tag=%r id=%r]"
      % (ev("document.activeElement.tagName"), ev("document.activeElement.id")))
ev("""(()=>{const e=new KeyboardEvent('keydown',{key:'/',bubbles:true,cancelable:true});
  document.body.dispatchEvent(e);})()""")
drain(0.6)
check("'/' focuses search when logged in", ev("document.activeElement.id"), "lookupId")
ev("""(()=>{const i=document.getElementById('lookupId');i.blur();
  document.body.focus && document.body.focus();})()""")
drain(0.4)
ev("""(()=>{const e=new KeyboardEvent('keydown',{key:'k',ctrlKey:true,bubbles:true,cancelable:true});
  document.body.dispatchEvent(e);})()""")
drain(0.6)
check("ctrl+k focuses search", ev("document.activeElement.id"), "lookupId")
# intended behaviour: shortcuts must not fire while the user is typing
ev("document.getElementById('commentInput').focus()")
ev("""(()=>{const e=new KeyboardEvent('keydown',{key:'k',ctrlKey:true,bubbles:true,cancelable:true});
  document.activeElement.dispatchEvent(e);})()""")
drain(0.5)
check("ctrl+k suppressed while typing", ev("document.activeElement.id"), "commentInput")
check("ctrl+r NOT hijacked (browser reload preserved)", ev(
  "(()=>{const e=new KeyboardEvent('keydown',{key:'r',ctrlKey:true,cancelable:true});"
  "document.activeElement.dispatchEvent(e);return e.defaultPrevented;})()"), False)

print(); print("=" * 78)
print("  page exceptions:", errors or "none")
print("RESULT:", "ALL PASSED" if not fails else f"{len(fails)} FAIL: {', '.join(fails)}")
print("=" * 78)
ws.close(); proc.terminate()