"""Drives the real page in headless Chrome: loads it, exercises every control, captures console errors."""
import json, subprocess, time, urllib.request, os, sys, socket
import websocket

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for stream in (sys.stderr,):
    try: stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9333
BASE = "http://127.0.0.1:8000"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_chrome_profile")
for f in ("token", "email", "user"):
    pass

proc = subprocess.Popen([
    CHROME, "--headless=new", f"--remote-debugging-port={PORT}", "--disable-gpu",
    "--no-first-run", "--no-default-browser-check", "--window-size=1400,1000",
    f"--user-data-dir={OUT}", "--remote-allow-origins=*", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ws_url = None
for _ in range(60):
    try:
        raw = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1).read()
        ws_url = json.loads(raw)["webSocketDebuggerUrl"]; break
    except Exception:
        time.sleep(0.5)
if not ws_url:
    print("could not reach chrome"); proc.kill(); sys.exit(1)

def _new_tab(url):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?{url}", method="PUT")
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

target = _new_tab(f"{BASE}/ui/")
ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=30,
                                 suppress_origin=True)
_id = [0]
def send(method, **params):
    _id[0] += 1
    ws.send(json.dumps({"id": _id[0], "method": method, "params": params}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == _id[0]:
            return msg.get("result", {})
def ev(expr, awaitp=False):
    r = send("Runtime.evaluate", expression=expr, awaitPromise=awaitp,
             returnByValue=True, userGesture=True)
    if "exceptionDetails" in r:
        return {"__error__": r["exceptionDetails"].get("text"),
                "desc": (r["exceptionDetails"].get("exception") or {}).get("description")}
    return r.get("result", {}).get("value")

errors, console = [], []
def drain(seconds=1.2):
    end = time.time() + seconds
    ws.settimeout(0.4)
    while time.time() < end:
        try:
            m = json.loads(ws.recv())
            if m.get("method") == "Runtime.exceptionThrown":
                d = m["params"]["exceptionDetails"]
                errors.append(d.get("exception", {}).get("description") or d.get("text"))
            if m.get("method") == "Runtime.consoleAPICalled" and m["params"]["type"] in ("error", "warning"):
                console.append(m["params"]["type"] + ": " +
                               " ".join(str(a.get("value")) for a in m["params"]["args"]))
        except Exception:
            pass
    ws.settimeout(30)

send("Runtime.enable"); send("Page.enable"); send("Log.enable")
drain(2.5)

print("=" * 78); print("A. page load"); print("=" * 78)
print("  title:", ev("document.title"))
print("  auth view visible:", ev("!document.getElementById('authView').hidden"))
print("  dash view hidden:", ev("document.getElementById('dashView').hidden"))
print("  script parsed:", ev("typeof window.establishSession === 'function'"))
print("  wireRoles ran (reg picker wired):", ev("typeof document.querySelector('#regRoles .role').onclick === 'function'"))
print("  role modal wired:", ev("typeof document.querySelector('#rolePick .role').onclick === 'function'"))

print(); print("=" * 78); print("B. tab switching"); print("=" * 78)
ev("document.getElementById('tabRegister').click()"); drain(0.4)
print("  register form shown:", ev("!document.getElementById('registerForm').hidden"))
print("  login form hidden:", ev("document.getElementById('loginForm').hidden"))
ev("document.getElementById('tabLogin').click()"); drain(0.4)
print("  back to login:", ev("!document.getElementById('loginForm').hidden"))
print("  role pick changes on click:", ev(
    "document.querySelectorAll('#regRoles .role')[1].click(),"
    "document.querySelector('#regRoles .role.active').dataset.role"))

print(); print("=" * 78); print("C. bad credentials -> real error must show (was 'Network error')"); print("=" * 78)
ev("""(()=>{const s=localStorage.clear();})()""")
ev("document.getElementById('loginEmail').value='nobody@nowhere.com';"
   "document.getElementById('loginPassword').value='whatever';"
   "document.getElementById('loginForm').requestSubmit();")
drain(2.5)
toasts = ev("Array.from(document.querySelectorAll('.toast')).map(t=>t.textContent)")
print("  toast shown:", toasts)
logs = ev("Array.from(document.querySelectorAll('#logList li')).map(l=>l.textContent)")
print("  console log:", logs[:2])

print(); print("=" * 78); print("D. invalid email -> validation error must show"); print("=" * 78)
ev("Array.from(document.querySelectorAll('.toast')).forEach(t=>t.remove())")
ev("document.getElementById('loginEmail').value='staff@test.com';"
   "document.getElementById('loginPassword').value='wrongpass';"
   "document.getElementById('loginForm').requestSubmit();")
drain(2.5)
print("  toast shown:", ev("Array.from(document.querySelectorAll('.toast')).map(t=>t.textContent)"))

print(); print("=" * 78); print("E. register a student -> session + role known"); print("=" * 78)
ev("Array.from(document.querySelectorAll('.toast')).forEach(t=>t.remove())")
ev("document.getElementById('tabRegister').click()")
import uuid
EMAIL = f"ui{uuid.uuid4().hex[:8]}@t.com"
ev(f"""(()=>{{
  document.getElementById('regName').value='Ui Tester';
  document.getElementById('regEmail').value='{EMAIL}';
  document.getElementById('regPassword').value='password123';
  document.querySelectorAll('#regRoles .role')[0].click();
  document.getElementById('registerForm').requestSubmit();
}})()""")
drain(3.0)
print("  logged in email:", EMAIL)
print("  dash visible:", ev("!document.getElementById('dashView').hidden"))
print("  chip name:", ev("document.getElementById('userName').textContent"))
print("  chip role:", ev("document.getElementById('userRole').textContent"))
print("  Report Issue button visible:", ev("!document.getElementById('newIssueBtn').hidden"))
print("  sidebar title:", ev("document.getElementById('listTitle').textContent"))
print("  localStorage keys:", ev("Object.keys(localStorage)"))

print(); print("=" * 78); print("F. create an issue through the modal"); print("=" * 78)
ev("document.getElementById('newIssueBtn').click()"); drain(0.5)
print("  modal open:", ev("document.getElementById('issueModal').open"))
print("  modal title:", ev("document.getElementById('modalTitle').textContent"))
ev("document.getElementById('fTitle').value='UI created light';"
   "document.getElementById('fDesc').value='lamp dead in lab 3';"
   "document.getElementById('fCategory').value='electricity';"
   "document.getElementById('fPriority').value='urgent';"
   "document.getElementById('issueForm').requestSubmit();")
drain(3.0)
print("  detail visible:", ev("!document.getElementById('issueDetail').hidden"))
print("  dId:", ev("document.getElementById('dId').textContent"))
print("  title:", ev("document.getElementById('dTitle').textContent"))
print("  status:", ev("document.getElementById('dStatus').textContent"))
print("  category:", ev("document.getElementById('dCategory').textContent"))
print("  priority:", ev("document.getElementById('dPriority').textContent + ' | cls=' + document.getElementById('dPriority').className"))
print("  owner:", ev("document.getElementById('dUser').textContent"))
print("  assignee:", ev("document.getElementById('dStaff').textContent"))
print("  owner may edit:", ev("!document.getElementById('editBtn').disabled"))
print("  owner may NOT start:", ev("document.getElementById('startBtn').disabled"))
print("  owner may NOT close(open):", ev("document.getElementById('closeBtn').disabled"))
print("  owner may comment:", ev("!document.getElementById('commentForm').hidden"))
print("  sidebar tracked:", ev("Array.from(document.querySelectorAll('#issueList li .t')).map(e=>e.textContent)"))
print("  flow done steps:", ev("Array.from(document.querySelectorAll('.step')).map(s=>s.dataset.s+':'+(s.classList.contains('done')?'done':'no'))"))

print(); print("=" * 78); print("G. comment round-trip"); print("=" * 78)
ev("document.getElementById('commentInput').value='hello from the UI';"
   "document.getElementById('commentForm').requestSubmit();")
drain(2.5)
print("  comments:", ev("Array.from(document.querySelectorAll('#commentList li')).map(l=>l.textContent)"))

print(); print("=" * 78); print("H. student tries to start staff-only action (button disabled)"); print("=" * 78)
print("  startBtn disabled:", ev("document.getElementById('startBtn').disabled"))

print(); print("=" * 78); print("I. 403 case: open an issue owned by someone else"); print("=" * 78)
import requests
t = requests.post(f"{BASE}/auth/login", data={"username": "staff@test.com", "password": "password123"}).json()["access_token"]
d = requests.get(f"{BASE}/openapi.json").json()["paths"]
other = 6
ev(f"""(()=>{{const i=document.getElementById('lookupId');i.value='{other}';
  document.getElementById('lookupForm').requestSubmit();}})()""")
drain(2.5)
print("  toast:", ev("Array.from(document.querySelectorAll('.toast')).map(t=>t.textContent)"))

print(); print("=" * 78); print("J. reload -> session restored, role remembered, no role modal"); print("=" * 78)
send("Page.reload"); drain(3.5)
print("  dash visible:", ev("!document.getElementById('dashView').hidden"))
print("  role:", ev("document.getElementById('userRole').textContent"))
print("  role modal NOT shown:", ev("!document.getElementById('roleModal').open"))
print("  tracked issues restored:", ev("Array.from(document.querySelectorAll('#issueList li .t')).map(e=>e.textContent)"))

print(); print("=" * 78); print("K. logout clears session"); print("=" * 78)
ev("document.getElementById('logoutBtn').click()"); drain(1.0)
print("  auth visible:", ev("!document.getElementById('authView').hidden"))
print("  token gone:", ev("localStorage.getItem('cf_token')===null"))

print(); print("=" * 78); print("L. invalid lookup id"); print("=" * 78)
print("=" * 78); print("captured page errors"); print("=" * 78)
print("  exceptions:", errors or "none")
print("  console errors/warnings:", console or "none")

ws.close(); proc.terminate()
print()
print("RESULT:", "NO RUNTIME EXCEPTIONS" if not errors else f"{len(errors)} EXCEPTION(S)")