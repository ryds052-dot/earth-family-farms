import unittest
from datetime import date, timedelta
from html.parser import HTMLParser
from unittest.mock import patch
from urllib.parse import urlsplit

from app import app


class SiteRouteTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_primary_pages_render_with_static_assets(self):
        for path in (
            "/",
            "/about",
            "/experiences",
            "/estates",
            "/stays",
            "/invest",
            "/estate-parcels",
            "/harvest",
            "/wholesale",
            "/vitals",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"/static/css/site.css", response.data)
                self.assertIn(b"/static/css/tailwind.css", response.data)
                self.assertNotIn(b"cdn.tailwindcss.com", response.data)

        for asset in (
            "/static/js/site.js",
            "/static/js/portal.js",
            "/static/css/tailwind.css",
            "/static/land-drone.mp4",
        ):
            with self.subTest(asset=asset):
                response = self.client.get(asset, buffered=False)
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_rendered_local_links_and_images_resolve(self):
        class LocalReferenceParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.references = []

            def handle_starttag(self, tag, attrs):
                attributes = dict(attrs)
                if tag == "a" and attributes.get("href", "").startswith("/"):
                    self.references.append(attributes["href"])
                if tag in {"img", "source"} and attributes.get("src", "").startswith("/"):
                    self.references.append(attributes["src"])

        for page in (
            "/",
            "/about",
            "/experiences",
            "/estates",
            "/stays",
            "/invest",
            "/harvest",
            "/vitals",
        ):
            response = self.client.get(page)
            parser = LocalReferenceParser()
            parser.feed(response.get_data(as_text=True))
            response.close()
            for reference in parser.references:
                with self.subTest(page=page, reference=reference):
                    resolved_path = urlsplit(reference).path
                    linked_response = self.client.get(resolved_path, buffered=False)
                    self.assertEqual(linked_response.status_code, 200)
                    linked_response.close()

    def test_investor_scenario_is_labeled_and_dynamically_configured(self):
        response = self.client.get("/invest")
        self.assertIn(b"Illustrative scenario only", response.data)
        self.assertIn(b"data-invest-calculator", response.data)
        self.assertIn(b"data-land-price=\"25000\"", response.data)
        self.assertIn(b"Verify", response.data)

    def test_investor_inquiry_validates_and_hands_off_to_concierge(self):
        response = self.client.post(
            "/invest",
            data={
                "name": "Investor",
                "email": "investor@example.com",
                "phone": "+1 876 555 0100",
                "acres": "4",
                "development_use": "permaculture",
                "request_type": "memorandum",
                "consent": "yes",
            },
        )
        self.assertEqual(response.status_code, 303)
        self.assertIn("wa.me/18762874304", response.headers["Location"])
        self.assertIn("4%20acre", response.headers["Location"])
        self.assertIn("Permaculture%20Venture", response.headers["Location"])

    def test_investor_inquiry_rejects_invalid_acreage_or_missing_consent(self):
        response = self.client.post(
            "/invest",
            data={
                "name": "Investor",
                "email": "investor@example.com",
                "phone": "+1 876 555 0100",
                "acres": "11",
                "development_use": "eco-villa",
                "request_type": "memorandum",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"between 1 and 10 acres", response.data)
        self.assertIn(b"understand the simulator uses illustrative assumptions", response.data)

    def test_harvest_dashboard_is_explicitly_sample_data(self):
        response = self.client.get("/harvest")
        self.assertEqual(response.status_code, 200)
        for label in (
            b"Sample seasonal pipeline",
            b"Apiary Honey (organic status unverified)",
            b"Root Botanicals",
            b"Breadfruit",
            b"Cacao",
            b"Seasonal Fruits",
        ):
            self.assertIn(label, response.data)

    def test_harvest_inquiry_requires_valid_crop_and_quantity(self):
        response = self.client.post(
            "/harvest",
            data={
                "company": "Resort",
                "contact_name": "Chef",
                "email": "chef@example.com",
                "phone": "+1 876 555 0100",
                "buyer_type": "resort-chef",
                "crops": ["breadfruit"],
                "quantity_breadfruit": "0",
                "delivery_window": "0-30",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"valid bulk quantity for Breadfruit", response.data)

    def test_harvest_bulk_inquiry_hands_off_structured_whatsapp_message(self):
        response = self.client.post(
            "/wholesale",
            data={
                "company": "Resort",
                "contact_name": "Chef",
                "email": "chef@example.com",
                "phone": "+1 876 555 0100",
                "buyer_type": "resort-chef",
                "crops": ["breadfruit", "cacao"],
                "quantity_breadfruit": "500",
                "quantity_cacao": "25.5",
                "delivery_window": "31-90",
                "notes": "Delivery to north coast",
            },
        )
        self.assertEqual(response.status_code, 303)
        location = response.headers["Location"]
        self.assertIn("wa.me/18762874304", location)
        self.assertIn("500", location)
        self.assertIn("25.5", location)
        self.assertIn("Resort", location)

    def test_vitals_are_labeled_as_simulated_and_render_on_homepage(self):
        for path in ("/", "/vitals"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Sanctuary Live Vitals", response.data)
            self.assertIn(b"Not connected to sensors", response.data)

    def test_stay_form_rejects_invalid_email_and_package(self):
        response = self.client.post(
            "/stays",
            data={
                "name": "Guest",
                "email": "not-an-email",
                "phone": "+1 876 555 0100",
                "package": "Unlisted offer",
                "date": "",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"valid email address", response.data)
        self.assertIn(b"available stay or experience", response.data)

    def test_stay_form_reports_missing_resend_configuration(self):
        with (
            patch("app.resend.api_key", None),
            patch("app.BOOKING_EMAIL", None),
            self.assertLogs("app", level="ERROR"),
        ):
            response = self.client.post("/stays", data=self.valid_stay_data())

        self.assertEqual(response.status_code, 503)
        self.assertIn(b"temporarily unavailable", response.data)

    def test_stay_form_sends_validated_and_escaped_inquiry(self):
        data = self.valid_stay_data()
        data["notes"] = "<script>alert('x')</script>"
        with (
            patch("app.resend.api_key", "test-key"),
            patch("app.BOOKING_EMAIL", "bookings@example.com"),
            patch("app.resend.Emails.send") as send_email,
        ):
            response = self.client.post("/stays", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your inquiry has been sent", response.data)
        params = send_email.call_args.args[0]
        self.assertEqual(params["reply_to"], data["email"])
        self.assertIn("&lt;script&gt;", params["html"])
        self.assertNotIn("<script>", params["html"])

    def test_stay_form_reports_email_provider_failure(self):
        with (
            patch("app.resend.api_key", "test-key"),
            patch("app.BOOKING_EMAIL", "bookings@example.com"),
            patch("app.resend.Emails.send", side_effect=RuntimeError("provider error")),
            self.assertLogs("app", level="ERROR"),
        ):
            response = self.client.post("/stays", data=self.valid_stay_data())

        self.assertEqual(response.status_code, 503)
        self.assertIn(b"could not send your request", response.data)

    def test_demo_rejects_unknown_villa(self):
        self.assertEqual(self.client.get("/demo/unknown-villa").status_code, 404)

    def test_demo_rejects_invalid_date_range(self):
        response = self.client.post(
            "/demo/upful",
            data={
                "guest_name": "Guest",
                "checkin": (date.today() + timedelta(days=3)).isoformat(),
                "checkout": (date.today() + timedelta(days=2)).isoformat(),
                "guests": "2 Adults",
                "upsell": "Decide Upon Arrival",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Check-out must be after check-in", response.data)

    def test_demo_creates_encoded_booking_handoff(self):
        checkin = date.today() + timedelta(days=3)
        checkout = checkin + timedelta(days=2)
        response = self.client.post(
            "/demo/upful",
            data={
                "guest_name": "Guest Name",
                "checkin": checkin.isoformat(),
                "checkout": checkout.isoformat(),
                "guests": "2 Adults",
                "upsell": "Decide Upon Arrival",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dates Ready to Lock In, Guest Name", response.data)
        self.assertIn(b"wa.me/18766031396", response.data)

    @staticmethod
    def valid_stay_data():
        return {
            "name": "Guest Name",
            "email": "guest@example.com",
            "phone": "+1 876 555 0100",
            "package": "Queen Cabin ($55/night)",
            "date": (date.today() + timedelta(days=3)).isoformat(),
            "notes": "Two guests",
        }


if __name__ == "__main__":
    unittest.main()
