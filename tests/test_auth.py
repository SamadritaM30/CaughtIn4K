from unittest.mock import patch

from auth_helpers import normalize_email, is_valid_email
from routes.auth import _is_verified_google_email
from tests.test_support import AQITestCase
from extensions import db
from models import User


class TestAuthentication(AQITestCase):

    # ── Auth-1 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_01_login_page_renders_for_unauthenticated_user(self):
        """Login page returns HTTP 200 for users with no active session."""

        # Any visitor who hasn't logged in should see the login page, not an error.
        print("\n[TC-AUTH-01] Sending GET /login with no active session...")
        response = self.client.get("/login")

        print(f"[TC-AUTH-01] Status code received: {response.status_code} (expected 200)")
        self.assertEqual(response.status_code, 200)

        # The response body should contain the word "login" (case-insensitive).
        print("[TC-AUTH-01] Checking response body contains 'login'...")
        self.assertIn(b"login", response.data.lower())
        print("[TC-AUTH-01] PASSED – login page rendered correctly for unauthenticated user.")

    # ── Auth-2 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_02_authenticated_user_redirected_from_login(self):
        """Logged-in user hitting /login is redirected to /dashboard."""

        # If a user is already logged in and visits /login, they should be
        # sent straight to the dashboard — no need to log in again.
        print("\n[TC-AUTH-02] Creating a Quality Operator user and logging in...")
        user = self.create_user("ops@example.com", "Quality Operator")
        self.login_as(user)

        print("[TC-AUTH-02] Sending GET /login as authenticated user...")
        response = self.client.get("/login")

        print(f"[TC-AUTH-02] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)

        print(f"[TC-AUTH-02] Redirect location: {response.headers['Location']} (expected /dashboard)")
        self.assertIn("/dashboard", response.headers["Location"])
        print("[TC-AUTH-02] PASSED – authenticated user correctly redirected to dashboard.")

    # ── Auth-3 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_03_google_oauth_initiated_state_stored_in_session(self):
        """GET /auth/google redirects to Google and stores CSRF state token."""

        # When Google OAuth is configured, clicking "Sign in with Google" should
        # redirect the user to Google's authorization page. A random state token
        # must also be stored in the session to prevent CSRF attacks later.
        print("\n[TC-AUTH-03] Configuring fake Google OAuth credentials...")
        self.app.config["GOOGLE_CLIENT_ID"] = "fake-client-id"
        self.app.config["GOOGLE_CLIENT_SECRET"] = "fake-secret"

        print("[TC-AUTH-03] Sending GET /auth/google...")
        response = self.client.get("/auth/google")

        print(f"[TC-AUTH-03] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)

        location = response.headers["Location"]
        print(f"[TC-AUTH-03] Redirect location: {location}")
        self.assertIn("accounts.google.com", location)

        # Verify the CSRF state token was saved in the session.
        with self.client.session_transaction() as sess:
            state_present = "google_oauth_state" in sess
            print(f"[TC-AUTH-03] 'google_oauth_state' in session: {state_present}")
            self.assertIn("google_oauth_state", sess)
        print("[TC-AUTH-03] PASSED – OAuth redirect issued and state token stored in session.")

    # ── Auth-4 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_04_callback_rejects_mismatched_csrf_state(self):
        """Tampered state token in callback causes redirect to /login with error flash."""

        # The callback compares the 'state' query param against what was stored
        # in the session. A mismatch means someone tampered with the request
        # (CSRF attack), so the login must be aborted.
        print("\n[TC-AUTH-04] Setting a known state token in session...")
        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "real_state_token"

        print("[TC-AUTH-04] Sending callback with a TAMPERED state value...")
        response = self.client.get(
            "/auth/google/callback?state=TAMPERED&code=somecode"
        )

        print(f"[TC-AUTH-04] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)

        print(f"[TC-AUTH-04] Redirect location: {response.headers['Location']} (expected /login)")
        self.assertIn("/login", response.headers["Location"])

        # Check the flash message warns the user the sign-in couldn't be verified.
        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        print(f"[TC-AUTH-04] Flash messages: {flashes}")
        self.assertTrue(any("could not be verified" in msg for _, msg in flashes))
        print("[TC-AUTH-04] PASSED – mismatched CSRF state correctly rejected.")

    # ── Auth-5 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_05_callback_blocks_unregistered_email(self):
        """Callback rejects a valid Google user whose email is not in the DB."""

        # Even if Google confirms the user's identity, they still need an account
        # in our system. Unknown emails must be turned away with a clear message.
        print("\n[TC-AUTH-05] Setting valid session state...")
        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "valid_state"

        fake_token = {"access_token": "tok"}
        fake_info = {
            "email": "stranger@example.com",
            "email_verified": True,
            "name": "Stranger",
        }
        print(f"[TC-AUTH-05] Mocking Google to return email: {fake_info['email']} (not in DB)...")

        with patch("routes.auth._exchange_google_code_for_tokens", return_value=fake_token), \
             patch("routes.auth._fetch_google_user_info", return_value=fake_info):
            response = self.client.get(
                "/auth/google/callback?state=valid_state&code=x"
            )

        print(f"[TC-AUTH-05] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        print(f"[TC-AUTH-05] Flash messages: {flashes}")
        self.assertTrue(any("not authorized" in msg for _, msg in flashes))
        print("[TC-AUTH-05] PASSED – unregistered email correctly blocked.")

    # ── Auth-6 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_06_bootstrap_admin_auto_provisioned(self):
        """Bootstrap admin email auto-creates a System Administrator account."""

        # Bootstrap admin emails are pre-configured so the very first admin
        # can log in without being manually created. On first OAuth login, the
        # system should auto-create their account with the Administrator role.
        admin_email = "newadmin@example.com"
        print(f"\n[TC-AUTH-06] Setting bootstrap admin email to: {admin_email}")
        self.app.config["GOOGLE_OAUTH_BOOTSTRAP_ADMIN_EMAILS"] = [admin_email]

        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "valid_state"

        fake_token = {"access_token": "tok"}
        fake_info = {"email": admin_email, "email_verified": True, "name": "New Admin"}
        print("[TC-AUTH-06] Mocking Google OAuth to return bootstrap admin email...")

        with patch("routes.auth._exchange_google_code_for_tokens", return_value=fake_token), \
             patch("routes.auth._fetch_google_user_info", return_value=fake_info):
            response = self.client.get(
                "/auth/google/callback?state=valid_state&code=x"
            )

        print(f"[TC-AUTH-06] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)
        print(f"[TC-AUTH-06] Redirect location: {response.headers['Location']} (expected /dashboard)")
        self.assertIn("/dashboard", response.headers["Location"])

        # Verify the user record was actually created in the database.
        with self.app.app_context():
            user = User.query.filter_by(username=admin_email).first()
            print(f"[TC-AUTH-06] User found in DB: {user is not None}, Role: {getattr(user, 'role', None)}")
            self.assertIsNotNone(user)
            self.assertEqual(user.role, "System Administrator")
        print("[TC-AUTH-06] PASSED – bootstrap admin auto-provisioned with correct role.")

    # ── Auth-7 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_07_unverified_google_email_rejected(self):
        """email_verified=false causes rejection even if email exists in DB."""

        # Google can return accounts whose email address hasn't been verified yet.
        # We must reject these — an unverified email is not a trustworthy identity.
        print("\n[TC-AUTH-07] Creating existing user in DB with unverified Google email...")
        self.create_user("ops@example.com", "Quality Operator")

        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "valid_state"

        fake_token = {"access_token": "tok"}
        # email_verified is False — Google hasn't confirmed ownership of this address.
        fake_info = {"email": "ops@example.com", "email_verified": False}
        print(f"[TC-AUTH-07] Mocking Google to return email_verified=False for {fake_info['email']}...")

        with patch("routes.auth._exchange_google_code_for_tokens", return_value=fake_token), \
             patch("routes.auth._fetch_google_user_info", return_value=fake_info):
            response = self.client.get(
                "/auth/google/callback?state=valid_state&code=x"
            )

        print(f"[TC-AUTH-07] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        print(f"[TC-AUTH-07] Flash messages: {flashes}")
        self.assertTrue(any("verified email" in msg for _, msg in flashes))
        print("[TC-AUTH-07] PASSED – unverified Google email correctly rejected.")

    # ── Auth-8 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_08_logout_clears_session_and_redirects(self):
        """Logout removes session state and redirects to /login."""

        # On logout, the user's session (including the OAuth state token) must
        # be fully cleared so no residual data can be reused.
        print("\n[TC-AUTH-08] Creating and logging in a user...")
        user = self.create_user("ops@example.com", "Quality Operator")
        self.login_as(user)

        # Manually set the OAuth state token to confirm it gets cleared.
        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "some_state"
        print("[TC-AUTH-08] Set google_oauth_state in session. Sending GET /logout...")

        response = self.client.get("/logout")

        print(f"[TC-AUTH-08] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)
        print(f"[TC-AUTH-08] Redirect location: {response.headers['Location']} (expected /login)")
        self.assertIn("/login", response.headers["Location"])

        with self.client.session_transaction() as sess:
            state_gone = "google_oauth_state" not in sess
            print(f"[TC-AUTH-08] 'google_oauth_state' removed from session: {state_gone}")
            self.assertNotIn("google_oauth_state", sess)
        print("[TC-AUTH-08] PASSED – session cleared and user redirected to login.")

    # ── Auth-9 ───────────────────────────────────────────────────────────────
    def test_TC_AUTH_09_protected_route_blocks_unauthenticated_access(self):
        """Unauthenticated GET /dashboard is redirected to /login."""

        # Every route that requires login must redirect anonymous users
        # to the login page rather than showing protected content.
        print("\n[TC-AUTH-09] Sending GET /dashboard with no session (unauthenticated)...")
        response = self.client.get("/dashboard")

        print(f"[TC-AUTH-09] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)

        print(f"[TC-AUTH-09] Redirect location: {response.headers['Location']} (expected /login)")
        self.assertIn("/login", response.headers["Location"])
        print("[TC-AUTH-09] PASSED – unauthenticated access to /dashboard correctly blocked.")

    # ── Auth-10 ──────────────────────────────────────────────────────────────
    def test_TC_AUTH_10_normalize_email_strips_and_lowercases(self):
        """normalize_email trims whitespace and returns lowercase."""

        # Emails must be normalised before storage and lookup so that
        # "USER@Example.COM" and "user@example.com" are treated as the same address.
        raw = "  USER@Example.COM "
        print(f"\n[TC-AUTH-10] Input email: '{raw}'")
        result = normalize_email(raw)
        print(f"[TC-AUTH-10] Normalised result: '{result}' (expected 'user@example.com')")
        self.assertEqual(result, "user@example.com")
        print("[TC-AUTH-10] PASSED – email correctly normalised.")

    # ── Auth-11 ──────────────────────────────────────────────────────────────
    def test_TC_AUTH_11_is_valid_email_rejects_malformed_address(self):
        """is_valid_email returns False for bad inputs and True for valid ones."""

        # The validator must reject obviously wrong addresses and accept well-formed ones.
        print("\n[TC-AUTH-11] Testing various email inputs against is_valid_email()...")

        test_cases = [
            ("not-an-email", False),
            ("",             False),
            (None,           False),
            ("valid@example.com", True),
        ]
        for value, expected in test_cases:
            result = is_valid_email(value)
            print(f"[TC-AUTH-11]   is_valid_email({value!r}) = {result} (expected {expected})")
            self.assertEqual(result, expected)
        print("[TC-AUTH-11] PASSED – all email validation cases correct.")

    # ── Auth-12 ──────────────────────────────────────────────────────────────
    def test_TC_AUTH_12_oauth_blocked_when_credentials_not_configured(self):
        """GET /auth/google is rejected with flash when OAuth is not set up."""

        # If the admin hasn't added Google OAuth credentials yet, the Sign-in
        # button should fail gracefully rather than throwing a server error.
        print("\n[TC-AUTH-12] Clearing Google OAuth credentials in app config...")
        self.app.config["GOOGLE_CLIENT_ID"] = ""
        self.app.config["GOOGLE_CLIENT_SECRET"] = ""

        print("[TC-AUTH-12] Sending GET /auth/google with missing credentials...")
        response = self.client.get("/auth/google")

        print(f"[TC-AUTH-12] Status code: {response.status_code} (expected 302)")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        print(f"[TC-AUTH-12] Flash messages: {flashes}")
        self.assertTrue(any("not configured" in msg for _, msg in flashes))
        print("[TC-AUTH-12] PASSED – OAuth correctly blocked when credentials are missing.")
