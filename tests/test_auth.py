from unittest.mock import patch

from auth_helpers import normalize_email, is_valid_email
from routes.auth import _is_verified_google_email
from tests.test_support import AQITestCase
from extensions import db
from models import User


class TestAuthentication(AQITestCase):

    # Auth-1
    def test_TC_AUTH_01_login_page_renders_for_unauthenticated_user(self):
        """Login page returns HTTP 200 for users with no active session."""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"login", response.data.lower())

    #  Auth-2 
    def test_TC_AUTH_02_authenticated_user_redirected_from_login(self):
        """Logged-in user hitting /login is redirected to /dashboard."""
        user = self.create_user("ops@example.com", "Quality Operator")
        self.login_as(user)
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.headers["Location"])

    #  Auth-3
    def test_TC_AUTH_03_google_oauth_initiated_state_stored_in_session(self):
        """GET /auth/google redirects to Google and stores CSRF state token."""
        self.app.config["GOOGLE_CLIENT_ID"] = "fake-client-id"
        self.app.config["GOOGLE_CLIENT_SECRET"] = "fake-secret"

        response = self.client.get("/auth/google")

        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.google.com", response.headers["Location"])
        with self.client.session_transaction() as sess:
            self.assertIn("google_oauth_state", sess)

    #  Auth-4
    def test_TC_AUTH_04_callback_rejects_mismatched_csrf_state(self):
        """Tampered state token in callback causes redirect to /login with error flash."""
        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "real_state_token"

        response = self.client.get(
            "/auth/google/callback?state=TAMPERED&code=somecode"
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        self.assertTrue(any("could not be verified" in msg for _, msg in flashes))

    #  Auth-5
    def test_TC_AUTH_05_callback_blocks_unregistered_email(self):
        """Callback rejects a valid Google user whose email is not in the DB."""
        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "valid_state"

        fake_token = {"access_token": "tok"}
        fake_info = {
            "email": "stranger@example.com",
            "email_verified": True,
            "name": "Stranger",
        }

        with patch("routes.auth._exchange_google_code_for_tokens", return_value=fake_token), \
             patch("routes.auth._fetch_google_user_info", return_value=fake_info):
            response = self.client.get(
                "/auth/google/callback?state=valid_state&code=x"
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        self.assertTrue(any("not authorized" in msg for _, msg in flashes))

    #  Auth-6
    def test_TC_AUTH_06_bootstrap_admin_auto_provisioned(self):
        """Bootstrap admin email auto-creates a System Administrator account."""
        admin_email = "newadmin@example.com"
        self.app.config["GOOGLE_OAUTH_BOOTSTRAP_ADMIN_EMAILS"] = [admin_email]

        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "valid_state"

        fake_token = {"access_token": "tok"}
        fake_info = {
            "email": admin_email,
            "email_verified": True,
            "name": "New Admin",
        }

        with patch("routes.auth._exchange_google_code_for_tokens", return_value=fake_token), \
             patch("routes.auth._fetch_google_user_info", return_value=fake_info):
            response = self.client.get(
                "/auth/google/callback?state=valid_state&code=x"
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.headers["Location"])
        with self.app.app_context():
            user = User.query.filter_by(username=admin_email).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role, "System Administrator")

    #      Auth-7
    def test_TC_AUTH_07_unverified_google_email_rejected(self):
        """email_verified=false causes rejection even if email exists in DB."""
        self.create_user("ops@example.com", "Quality Operator")

        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "valid_state"

        fake_token = {"access_token": "tok"}
        fake_info = {"email": "ops@example.com", "email_verified": False}

        with patch("routes.auth._exchange_google_code_for_tokens", return_value=fake_token), \
             patch("routes.auth._fetch_google_user_info", return_value=fake_info):
            response = self.client.get(
                "/auth/google/callback?state=valid_state&code=x"
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        self.assertTrue(any("verified email" in msg for _, msg in flashes))

    #    Auth-8
    def test_TC_AUTH_08_logout_clears_session_and_redirects(self):
        """Logout removes session state and redirects to /login."""
        user = self.create_user("ops@example.com", "Quality Operator")
        self.login_as(user)
        with self.client.session_transaction() as sess:
            sess["google_oauth_state"] = "some_state"

        response = self.client.get("/logout")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        with self.client.session_transaction() as sess:
            self.assertNotIn("google_oauth_state", sess)

    #     Auth-9
    def test_TC_AUTH_09_protected_route_blocks_unauthenticated_access(self):
        """Unauthenticated GET /dashboard is redirected to /login."""
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    #     Auth-10
    def test_TC_AUTH_10_normalize_email_strips_and_lowercases(self):
        """normalize_email trims whitespace and returns lowercase."""
        self.assertEqual(normalize_email("  USER@Example.COM "), "user@example.com")

    #     Auth-11
    def test_TC_AUTH_11_is_valid_email_rejects_malformed_address(self):
        """is_valid_email returns False for bad inputs and True for valid ones."""
        self.assertFalse(is_valid_email("not-an-email"))
        self.assertFalse(is_valid_email(""))
        self.assertFalse(is_valid_email(None))
        self.assertTrue(is_valid_email("valid@example.com"))

    #      Auth-12
    def test_TC_AUTH_12_oauth_blocked_when_credentials_not_configured(self):
        """GET /auth/google is rejected with flash when OAuth is not set up."""
        self.app.config["GOOGLE_CLIENT_ID"] = ""
        self.app.config["GOOGLE_CLIENT_SECRET"] = ""

        response = self.client.get("/auth/google")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        self.assertTrue(any("not configured" in msg for _, msg in flashes))
