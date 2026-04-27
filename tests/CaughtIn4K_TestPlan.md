# CaughtIn4K — Software Test Plan & Test Cases
**Version 1.0 | April 2026**

---

## Part A — Test Plan

### 1. Objective of Testing

Validate that CaughtIn4K behaves correctly, securely, and reliably end-to-end:

- Ensure only authorised users can access protected routes (RBAC / Google OAuth).
- Confirm the ML inference pipeline meets ≥ 90% accuracy and ≤ 2 s/image latency.
- Verify the Human-in-the-Loop review workflow captures feedback and persists it correctly.
- Validate that the online retrain trigger fires at the correct threshold and marks affected records.
- Detect regressions after every incremental model update or code change.

---

### 2. Scope

| Module | Features Covered | In / Out of Scope |
|---|---|---|
| Authentication & RBAC | Google OAuth flow, CSRF state validation, email verification, session lifecycle, role-based route access |  In scope |
| ML Inference (Inspection) | Model path resolution, background thread, defect scoring, heatmap generation, DB persistence, status polling |  In scope |
| Human Review & Retrain | Submit review, false-negative mask redirect, mask storage, retrain threshold check, retrain thread launch |  In scope |
| Admin User Management | Create user, restricted to System Administrator role only |  In scope |
| Model Training | Dataset structure validation, background training thread, status polling |  In scope |
| Dashboard & History | Inspection history listing, owner-only access control on history detail |  In scope |
| Hardware / Camera | Physical camera capture, edge-device deployment |  Out of scope |

---

### 3. Types of Testing

| Type | Description | Target |
|---|---|---|
| Unit | Individual functions tested in isolation with mocked dependencies — email validators, auth helpers, private route methods. | `auth_helpers.py`, `routes/auth.py` |
| Integration | Multiple components exercised together through the Flask test client — routes, DB models, and session management. | `routes/`, `models.py`, `extensions.py` |
| Black-Box | Tests driven purely by external behaviour: HTTP status codes, redirect locations, and flash messages. | `test_auth.py` (all 12 cases) |
| White-Box | Branch-level coverage of internal logic — CSRF check, model-path fallback, retrain threshold counter. | `test_white_box.py` |
| Security | CSRF state-token tampering, unauthorised role access, cross-operator history access denial. | `routes/auth.py`, `admin.py`, `dashboard.py` |
| Performance | Inference latency ≤ 2 s/image and FPS metrics recorded and stored in `InspectionRun`. | `run_model.py`, `routes/ml.py` |
| Regression | Full test suite re-executed after every incremental model update or code commit. | All modules |

---

### 4. Tools

| Tool | Purpose | Notes |
|---|---|---|
| Python unittest | Core test runner and assertion library | Built-in; used across all test files |
| Flask Test Client | Simulates HTTP requests without a live server | Configured in `AQITestCase` (`test_support.py`) |
| unittest.mock | Patches Google OAuth network calls and retrain threads | Avoids external dependencies in CI |
| SQLite in-memory | Isolated test database; created and torn down per test | No external DB server required |
| pytest (optional) | Richer reporting, parallel execution, HTML coverage output | Compatible via standard unittest discovery |
| coverage.py | Measures statement & branch coverage | `coverage run -m pytest; coverage report -m` |

---

### 5. Entry and Exit Criteria

| Area | Entry Criteria | Exit Criteria |
|---|---|---|
| Environment | Python 3.10+, Flask & dependencies installed; SQLite available; `AQITestCase.setUp()` completes without error. | All environments torn down cleanly; no residual test data. |
| Code Readiness | Code committed, review-approved, no merge conflicts, all modules importable. | No P1/P2 defects open; all defects documented with severity and owner. |
| Coverage | Test cases reviewed and approved; `AQITestCase` helpers verified as working. | ≥ 80% statement coverage on `routes/` & `auth_helpers.py`; 100% of auth and RBAC paths covered. |
| Pass Rate | At least one full baseline run completed with no import errors. | ≥ 95% of planned test cases pass; every failure has a documented root-cause. |

---

## Part B — Test Cases

**Module Under Test:** Authentication (`routes/auth.py` & `auth_helpers.py`)

The Authentication module is the security gateway to all other features — it handles Google OAuth, CSRF protection, email validation, session management, and role-based access. All 12 test cases are listed below.

---

| TC ID | Scenario / Description | Input Data | Expected Output | Actual Output | Status |
|---|---|---|---|---|---|
| TC-AUTH-01 | Login page renders for unauthenticated user | `GET /login` (no session) | HTTP 200; `login.html` served | HTTP 200; login page displayed |  Pass |
| TC-AUTH-02 | Authenticated user hitting `/login` is redirected to dashboard | `GET /login` (active session) | HTTP 302 → `/dashboard` | HTTP 302 → `/dashboard` |  Pass |
| TC-AUTH-03 | Google OAuth flow initiated; state token stored in session | `GET /auth/google` (OAuth configured, not logged in) | HTTP 302 → `accounts.google.com`; state stored in session | Redirect issued; state stored |  Pass |
| TC-AUTH-04 | Callback rejects mismatched CSRF state token | `GET /auth/google/callback?state=TAMPERED&code=x` (session state differs) | HTTP 302 → `/login`; flash "could not be verified" | HTTP 302 → `/login`; correct flash shown |  Pass |
| TC-AUTH-05 | Callback blocks Google account not registered in the system | Valid OAuth code for email not in `User` table | HTTP 302 → `/login`; flash "not authorized yet" | HTTP 302 → `/login`; no session created |  Pass |
| TC-AUTH-06 | Bootstrap admin email auto-provisions System Administrator user | Valid OAuth code for email in `GOOGLE_OAUTH_BOOTSTRAP_ADMIN_EMAILS` | User created with `role='System Administrator'`; redirect → `/dashboard` | User persisted; redirect and success flash confirmed |  Pass |
| TC-AUTH-07 | Unverified Google email is rejected | `userinfo` payload with `email_verified=false` | HTTP 302 → `/login`; flash "must have a verified email" | HTTP 302 → `/login`; correct flash displayed |  Pass |
| TC-AUTH-08 | Logout clears session and redirects to login | `GET /logout` (authenticated) | Session cleared; HTTP 302 → `/login` | Session cleared; redirect confirmed |  Pass |
| TC-AUTH-09 | Protected route blocks unauthenticated access | `GET /dashboard` (no session) | HTTP 302 → `/login` | HTTP 302 → `/login` |  Pass |
| TC-AUTH-10 | `normalize_email` trims whitespace and lowercases | `normalize_email('  USER@Example.COM ')` | Returns `'user@example.com'` | Returns `'user@example.com'` |  Pass |
| TC-AUTH-11 | `is_valid_email` rejects malformed address | `is_valid_email('not-an-email')` | Returns `False` | Returns `False` |  Pass |
| TC-AUTH-12 | OAuth initiation blocked when credentials not configured | `GET /auth/google` (`CLIENT_ID`/`SECRET` empty in config) | HTTP 302 → `/login`; flash "not configured yet" | HTTP 302 → `/login`; correct flash shown |  Pass |

**Result: 12 / 12 Passed (100%)**
