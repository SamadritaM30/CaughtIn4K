import base64
from pathlib import Path

from extensions import db
from models import HumanReview, User
from tests.test_support import AQITestCase


ONE_PIXEL_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAusB9Y9l9O8AAAAASUVORK5CYII="
)


class BlackBoxTests(AQITestCase):
    def test_dashboard_requires_authentication(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_admin_can_create_user(self):
        admin = self.create_user("admin@example.com", "System Administrator")
        self.login_as(admin)

        response = self.client.post(
            "/create_user",
            data={"email": "operator@example.com", "role": "Quality Operator"},
        )

        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            created = User.query.filter_by(username="operator@example.com").first()
            self.assertIsNotNone(created)
            self.assertEqual(created.role, "Quality Operator")

    def test_non_admin_cannot_create_user(self):
        operator = self.create_user("operator@example.com", "Quality Operator")
        self.login_as(operator)

        response = self.client.post(
            "/create_user",
            data={"email": "newuser@example.com", "role": "Quality Operator"},
        )

        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            created = User.query.filter_by(username="newuser@example.com").first()
            self.assertIsNone(created)

    def test_operator_run_inspection_without_model_is_rejected(self):
        operator = self.create_user("operator@example.com", "Quality Operator")
        self.login_as(operator)

        response = self.client.post(
            "/run_inspection",
            data={"item_name": "bottle", "test_folder": "missing/test/path"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.headers["Location"])

        with self.client.session_transaction() as session:
            flashes = session.get("_flashes", [])
        self.assertTrue(any("Model not found" in message for _, message in flashes))

    def test_history_detail_is_visible_only_to_owning_operator(self):
        owner = self.create_user("owner@example.com", "Quality Operator")
        other = self.create_user("other@example.com", "Quality Operator")
        run = self.create_inspection_run(owner.id)
        self.create_inspection_result(run.id, img_name="000.png")
        self.create_review(predicted_label="GOOD", reviewed=True, is_correct=True, human_label="GOOD")

        self.login_as(owner)
        allowed = self.client.get(f"/history/{run.id}")
        self.assertEqual(allowed.status_code, 200)

        self.login_as(other)
        denied = self.client.get(f"/history/{run.id}")
        self.assertEqual(denied.status_code, 403)

    def test_false_negative_review_redirects_to_mask_drawing(self):
        operator = self.create_user("operator@example.com", "Quality Operator")
        self.login_as(operator)
        review = self.create_review(predicted_label="GOOD")

        response = self.client.post(
            f"/submit_review/{review.id}",
            data={"is_correct": "no", "correct_label": "DEFECTIVE"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/draw_mask/{review.id}", response.headers["Location"])

    def test_submit_mask_saves_file_and_marks_reviewed(self):
        operator = self.create_user("operator@example.com", "Quality Operator")
        self.login_as(operator)
        review = self.create_review(
            predicted_label="GOOD",
            reviewed=False,
            is_correct=False,
            human_label="DEFECTIVE",
        )

        response = self.client.post(
            f"/submit_mask/{review.id}",
            data={"mask_data": f"data:image/png;base64,{ONE_PIXEL_PNG}"},
        )

        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            refreshed = db.session.get(HumanReview, review.id)
            self.assertTrue(refreshed.reviewed)
            self.assertEqual(refreshed.mask_path, f"masks/mask_{review.id}.png")

        saved_mask = Path(self.temp_root) / "static" / "masks" / f"mask_{review.id}.png"
        self.assertTrue(saved_mask.exists())
