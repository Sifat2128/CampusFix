"""Executes the real permission/format logic from app.js against LIVE backend responses."""
import requests, json, re, uuid

BASE = "http://127.0.0.1:8000"
P, S = requests.post, requests.get
def hdr(t): return {"Authorization": f"Bearer {t}"}
def tok(e, p="password123"):
    return P(f"{BASE}/auth/login", data={"username": e, "password": p}).json()["access_token"]
def mk(name, role):
    e = f"{role}{uuid.uuid4().hex[:8]}@t.com"
    r = P(f"{BASE}/auth/register", json={"name": name, "email": e, "password": "password123", "role": role})
    assert r.status_code == 200, r.text
    return e, tok(e)

# ---- exact ports of the app.js helpers under test ----
pretty = lambda v: "\u2014" if v is None else str(v).replace("_", " ")
cap    = lambda v: "\u2014" if v in (None, "") else str(v)[0].upper() + str(v)[1:]
ORDER  = ["open", "in_progress", "resolved", "closed"]

def read_detail(data, status):
    d = data.get("detail") if isinstance(data, dict) else None
    if isinstance(d, str): return d
    if isinstance(d, list):
        return "; ".join(f"{'/'.join(str(x) for x in (i.get('loc') or [])[1:]) or 'body'}: {i.get('msg','invalid')}" for i in d)
    if d: return json.dumps(d)
    return f"Request failed (HTTP {status})"

def apply_permissions(i, role, me):
    """port of app.js applyPermissions(); returns the *disabled* flags"""
    status = i.get("status")
    know_who = bool(me)
    owner = know_who and i.get("user") == me
    assigned = know_who and i.get("assigned_employee") == me
    deny = lambda permitted: (not permitted) if know_who else False      # disabled
    allow = lambda permitted: permitted if know_who else True           # permitted
    return {
      "start":   True if role != "staff" else deny(assigned and status == "open"),
      "resolve": True if role != "staff" else deny(assigned and status in ("open", "in_progress")),
      "close":   True if role != "student" else deny(owner and status == "resolved"),
      "edit":    (False if role == "admin"
                  else deny(owner and status == "open") if role == "student" else True),
      "comment_visible": (False if role == "faculty" else allow(owner or assigned)),
    }

fails = []
def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label:52} got={got!r}")
    if not ok:
        print(f"        expected {want!r}")
        fails.append(label)

print("=" * 78); print("TEST 1 — read_detail(): real backend errors surface verbatim"); print("=" * 78)
check("duplicate email 409", read_detail(P(f"{BASE}/auth/register", json={"name":"D","email":"student@test.com","password":"password123","role":"student"}).json(), 409), "A user with this email already exists")
check("ghost login 404",   read_detail(P(f"{BASE}/auth/login", data={"username":f"no{uuid.uuid4().hex[:6]}@t.com","password":"x"}).json(), 404), "Intended User not Found")
check("bad password 401",  read_detail(P(f"{BASE}/auth/login", data={"username":"student@test.com","password":"WRONG"}).json(), 401), "Invalid Credentials")
check("422 validation",    read_detail(P(f"{BASE}/auth/register", json={"name":"X","email":"bad","password":"1"}).json(), 422), "email: value is not a valid email address: An email address must have an @-sign.; password: String should have at least 6 characters; role: Field required")
check("no-detail fallback", read_detail({}, 500), "Request failed (HTTP 500)")

print(); print("=" * 78); print("TEST 2 — pretty()/cap() survive null (the old crash)"); print("=" * 78)
check("pretty(None)", pretty(None), "\u2014")
check("cap(None)",    cap(None),    "\u2014")
check("pretty('in_progress')", pretty("in_progress"), "in progress")
check("cap('urgent')", cap("urgent"), "Urgent")

print(); print("=" * 78); print("TEST 3 — flow index for every real status (JS indexOf semantics)"); print("=" * 78)
js_index_of = lambda arr, v: arr.index(v) if v in arr else -1   # JS Array.indexOf
for s, want in [("open",0),("in_progress",1),("resolved",2),("closed",3),("assigned",-1),("bogus",-1),(None,-1)]:
    check(f"indexOf({s!r})", js_index_of(ORDER, s), want)

print(); print("=" * 78); print("TEST 4 — permissions agree with the API, per role"); print("=" * 78)
su, st_ = mk("Stu", "student")
fu, ft_ = mk("Fac", "faculty")
ad, at_ = mk("Ada", "admin")
wu, wt_ = mk("Wor", "student")   # a second student, to test non-owner

r = P(f"{BASE}/issues/create", json={"title":"perm probe","description":"d","category":"water","priority":"high"}, headers=hdr(st_))
iid = r.json()["id"]
issue = S(f"{BASE}/issues/{iid}", headers=hdr(st_)).json()
print(f"  issue #{iid}  owner={issue['user']!r} assignee={issue['assigned_employee']!r} status={issue['status']!r}")

# staff account is whoever the API auto-picked; find them via the staff endpoint logic
staff_name = issue["assigned_employee"]
su2, st2 = mk(staff_name + "X", "staff")  # a *different* staff, must be denied

# NOTE: apply_permissions returns the *disabled* flags, so True == button unusable.

print("\n  -- owner student, open --")
check("Stu start disabled",   apply_permissions(issue,"student","Stu")["start"],   True)
check("Stu resolve disabled", apply_permissions(issue,"student","Stu")["resolve"], True)
check("Stu close disabled",   apply_permissions(issue,"student","Stu")["close"],   True)
check("Stu edit enabled",     apply_permissions(issue,"student","Stu")["edit"],    False)
check("Stu may comment",      apply_permissions(issue,"student","Stu")["comment_visible"], True)

print("\n  -- different student, open --")
check("Wor start disabled",   apply_permissions(issue,"student","Wor")["start"],   True)
check("Wor edit disabled",    apply_permissions(issue,"student","Wor")["edit"],    True)
check("Wor comment hidden",   apply_permissions(issue,"student","Wor")["comment_visible"], False)

print("\n  -- admin, open --")
check("Ada start disabled",   apply_permissions(issue,"admin","Ada")["start"],   True)
check("Ada edit enabled",     apply_permissions(issue,"admin","Ada")["edit"],    False)
check("Ada comment hidden",   apply_permissions(issue,"admin","Ada")["comment_visible"], False)  # backend rejects

print("\n  -- faculty, open --")
check("Fac start disabled",   apply_permissions(issue,"faculty","Fac")["start"],   True)
check("Fac comment hidden",   apply_permissions(issue,"faculty","Fac")["comment_visible"], False)

print("\n  -- assigned staff, open --")
check("assigned start enabled",   apply_permissions(issue,"staff",staff_name)["start"],   False)
check("assigned resolve enabled", apply_permissions(issue,"staff",staff_name)["resolve"], False)
print("\n  -- a DIFFERENT staff (server rejects these too) --")
check("other staff start disabled",   apply_permissions(issue,"staff","SomeoneElse")["start"],   True)
check("other staff resolve disabled", apply_permissions(issue,"staff","SomeoneElse")["resolve"], True)

print("\n  -- name unknown as staff: start/resolve defer to server, close/edit blocked by role --")
check("unknown-name start deferred",   apply_permissions(issue,"staff","")["start"],   False)
check("unknown-name resolve deferred", apply_permissions(issue,"staff","")["resolve"], False)
check("unknown-name close blocked (role)",   apply_permissions(issue,"staff","")["close"], True)
check("unknown-name edit blocked (role)",    apply_permissions(issue,"staff","")["edit"],  True)
print("  -- name unknown as student: everything role-allowed defers --")
check("unknown student close deferred", apply_permissions(issue,"student","")["close"],  False)
check("unknown student edit deferred",  apply_permissions(issue,"student","")["edit"],   False)
check("unknown student comment shown",  apply_permissions(issue,"student","")["comment_visible"], True)

print("\n  -- cross-check against the live API --")
check("API: other staff read -> 403",  S(f"{BASE}/issues/{iid}", headers=hdr(st2)).status_code, 403)
check("API: admin read       -> 200",  S(f"{BASE}/issues/{iid}", headers=hdr(at_)).status_code, 200)
check("API: admin comment    -> 403",  P(f"{BASE}/issues/{iid}/comments", json={"content":"x"}, headers=hdr(at_)).status_code, 403)
check("API: faculty comment  -> 403",  P(f"{BASE}/issues/{iid}/comments", json={"content":"x"}, headers=hdr(ft_)).status_code, 403)
check("API: owner comment    -> 200",  P(f"{BASE}/issues/{iid}/comments", json={"content":"x"}, headers=hdr(st_)).status_code, 200)
check("API: staff create     -> 403",  P(f"{BASE}/issues/create", json={"title":"x","description":"d","category":"other","priority":"low"}, headers=hdr(st2)).status_code, 403)
check("API: missing issue    -> 404",  S(f"{BASE}/issues/999999", headers=hdr(st_)).status_code, 404)

print("\n  -- status-driven gates --")
issue["status"] = "resolved"
check("owner close enabled (resolved)",   apply_permissions(issue,"student","Stu")["close"],   False)
check("owner edit disabled (resolved)",   apply_permissions(issue,"student","Stu")["edit"],    True)
check("assigned resolve disabled (resolved)", apply_permissions(issue,"staff",staff_name)["resolve"], True)
issue["status"] = "in_progress"
check("owner edit disabled (in_progress)", apply_permissions(issue,"student","Stu")["edit"],    True)
check("assigned resolve enabled (in_progress)", apply_permissions(issue,"staff",staff_name)["resolve"], False)
issue["status"] = "closed"
check("owner close disabled (closed)", apply_permissions(issue,"student","Stu")["close"], True)
check("assigned resolve disabled (closed)", apply_permissions(issue,"staff",staff_name)["resolve"], True)
check("owner edit disabled (closed)", apply_permissions(issue,"student","Stu")["edit"], True)

print(); print("=" * 78)
print(f"RESULT: {'ALL TESTS PASSED' if not fails else str(len(fails)) + ' FAILURE(S): ' + ', '.join(fails)}")
print("=" * 78)