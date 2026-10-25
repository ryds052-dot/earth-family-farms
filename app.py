import html
import logging
import os
import re
import urllib.parse
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Flask, abort, redirect, render_template, request, url_for
import resend
from resend.exceptions import ResendError

VILLA_PROSPECTS = {
    "upful": {
        "name": "Upful Villa",
        "location": "Treasure Beach, St. Elizabeth",
        "tagline": "Private Beachfront Sanctuary & In-House Culinary Experience",
        "rate": "$450 USD / night",
        "whatsapp": "18766031396",
        "upsell_label": "Select Arrival Meal (Prepared by Chevell)",
        "upsells": [
            "Traditional Curry Goat & Rice and Peas",
            "Fresh Escoveitch Fish & Bammy",
            "Braised Oxtail Dinner",
            "Decide Upon Arrival"
        ]
    },
    "fantasy": {
        "name": "Villas Fantasy & Beachnut",
        "location": "Priory, St. Ann",
        "tagline": "11-Bedroom Gated Private Beachfront Compound",
        "rate": "Custom Group Rate",
        "whatsapp": "18760000000", # Replace with their number or yours for testing
        "upsell_label": "Select Group Concierge Add-Ons",
        "upsells": [
            "Both Villas (11 Bedrooms Total) + Private Chef",
            "Villa Fantasy Only (6 Bedrooms) + Airport Transfer",
            "Beachnut Only (5 Bedrooms)",
            "Standard Villa Rental Only"
        ]
    },
    "prospect": {
        "name": "Prospect Estate & Villas",
        "location": "Ocho Rios, St. Ann",
        "tagline": "Historic 1,000-Acre Oceanfront Luxury Estate",
        "rate": "Estate Tier Pricing",
        "whatsapp": "18760000000",
        "upsell_label": "Add VIP Estate Excursion Package",
        "upsells": [
            "Private ATV & Camel Safari Tour",
            "Full In-Villa Chef & Butler Service",
            "Wedding / Corporate Event Inquiry",
            "Accommodation Only"
        ]
    }
}

BOOKING_PACKAGES = {
    "Queen Cabin ($55/night)",
    "Cannabis & Exotic Fruit Tour ($30/person)",
    "Collier Gully River Hike ($20/person)",
    "Full Sanctuary Package",
}
GUEST_OPTIONS = {"2 Adults", "4-6 Guests", "7+ Guests"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[0-9+(). \-]{7,25}$")
CONCIERGE_WHATSAPP = "18762874304"
LAND_PRICE_PER_ACRE_USD = 25000
ANNUAL_LAND_APPRECIATION_PERCENT = 5
INVESTMENT_USES = {
    "eco-villa": {
        "label": "Eco-Villa Retreat",
        "gross_rental_yield_percent": 8,
        "summary": "Illustrative gross bookings against land acquisition basis.",
    },
    "homestead": {
        "label": "Off-Grid Homestead",
        "gross_rental_yield_percent": 5,
        "summary": "Illustrative gross rental income against land acquisition basis.",
    },
    "permaculture": {
        "label": "Permaculture Venture",
        "gross_rental_yield_percent": 4,
        "summary": "Illustrative gross lease income against land acquisition basis.",
    },
}
HARVEST_CROPS = {
    "honey": {
        "name": "Apiary Honey (organic status unverified)",
        "unit": "litres",
        "sample_volume": 120,
        "planning_window": "Sample planning window · Q4–Q1",
    },
    "root-botanicals": {
        "name": "Root Botanicals",
        "unit": "kilograms",
        "sample_volume": 350,
        "planning_window": "Sample planning window · seasonal",
    },
    "breadfruit": {
        "name": "Breadfruit",
        "unit": "kilograms",
        "sample_volume": 600,
        "planning_window": "Sample planning window · Q3–Q4",
    },
    "cacao": {
        "name": "Cacao",
        "unit": "kilograms",
        "sample_volume": 180,
        "planning_window": "Sample planning window · Q1–Q2",
    },
    "seasonal-fruits": {
        "name": "Seasonal Fruits",
        "unit": "kilograms",
        "sample_volume": 450,
        "planning_window": "Sample planning window · varies by crop",
    },
}
BUYER_TYPES = {
    "resort-chef": "Resort / Hotel Chef",
    "boutique-brand": "Boutique Brand",
    "export-distributor": "Export Distributor",
    "other": "Other",
}
INVESTOR_REQUEST_TYPES = {
    "memorandum": "Confidential Offering Memorandum",
    "parcel": "Parcel Reservation Discussion",
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.logger.setLevel(logging.INFO)

resend.api_key = os.environ.get("RESEND_API_KEY")
BOOKING_EMAIL = os.environ.get("BOOKING_EMAIL")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")


def parse_booking_date(value):
    if not value:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed_date


def build_whatsapp_url(message):
    return f"https://wa.me/{CONCIERGE_WHATSAPP}?text={urllib.parse.quote(message)}"


def validate_contact(name, email, phone):
    errors = []
    if (
        not name
        or len(name) > 100
        or any(ord(character) < 32 for character in name)
    ):
        errors.append("Enter a name (up to 100 characters).")
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        errors.append("Enter a valid email address.")
    if (
        not PHONE_PATTERN.fullmatch(phone)
        or not any(character.isdigit() for character in phone)
    ):
        errors.append("Enter a valid phone or WhatsApp number.")
    return errors


def get_vitals_demo():
    return {
        "water_output": "1,840",
        "carbon_offset": "2.7",
        "canopy_preservation": "86",
        "temperature": "28",
        "humidity": "78",
        "wind": "12",
    }


def render_whatsapp_error(template, form_data, error, status_code=400, **context):
    return render_template(
        template,
        form_data=form_data,
        error=error,
        **context,
    ), status_code


@app.route("/")
def home():
    return render_template("index.html", vitals=get_vitals_demo())


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/experiences")
def experiences():
    return render_template("experiences.html")


@app.route("/estates")
def estates():
    return render_template("estates.html")


@app.route("/invest", methods=["GET", "POST"])
@app.route("/estate-parcels", methods=["GET", "POST"])
def invest():
    form_data = {
        "name": "",
        "email": "",
        "phone": "",
        "acres": "1",
        "development_use": "eco-villa",
        "request_type": "memorandum",
        "consent": "",
    }
    if request.method == "GET":
        return render_template(
            "invest.html",
            form_data=form_data,
            investment_uses=INVESTMENT_USES,
            land_price_per_acre=LAND_PRICE_PER_ACRE_USD,
            appreciation_percent=ANNUAL_LAND_APPRECIATION_PERCENT,
        )

    form_data.update({
        key: request.form.get(key, "").strip()
        for key in ("name", "email", "phone", "acres", "development_use", "request_type", "consent")
    })
    errors = validate_contact(
        form_data["name"], form_data["email"], form_data["phone"]
    )
    if not re.fullmatch(r"[0-9]{1,2}", form_data["acres"]) or not 1 <= int(
        form_data["acres"] or "0"
    ) <= 10:
        errors.append("Choose between 1 and 10 acres.")
    if form_data["development_use"] not in INVESTMENT_USES:
        errors.append("Select an available development use.")
    if form_data["request_type"] not in INVESTOR_REQUEST_TYPES:
        errors.append("Select a valid inquiry type.")
    if form_data["consent"] != "yes":
        errors.append("Confirm that you understand this is an illustrative, non-binding inquiry.")
    if errors:
        return render_whatsapp_error(
            "invest.html",
            form_data,
            " ".join(errors),
            investment_uses=INVESTMENT_USES,
            land_price_per_acre=LAND_PRICE_PER_ACRE_USD,
            appreciation_percent=ANNUAL_LAND_APPRECIATION_PERCENT,
        )

    use_label = INVESTMENT_USES[form_data["development_use"]]["label"]
    request_label = INVESTOR_REQUEST_TYPES[form_data["request_type"]]
    message = (
        "Earth Family Farms - confidential estate inquiry\n"
        f"Request: {request_label}\n"
        f"Name: {form_data['name']}\n"
        f"Email: {form_data['email']}\n"
        f"Phone / WhatsApp: {form_data['phone']}\n"
        f"Indicative parcel size: {'10+ (minimum 10)' if form_data['acres'] == '10' else form_data['acres']} acre(s)\n"
        f"Intended use: {use_label}\n"
        "Acknowledged illustrative, non-binding scenario."
    )
    return redirect(build_whatsapp_url(message), code=303)


@app.route("/harvest", methods=["GET", "POST"])
@app.route("/wholesale", methods=["GET", "POST"])
def harvest():
    form_data = {
        "company": "",
        "contact_name": "",
        "email": "",
        "phone": "",
        "buyer_type": "",
        "crops": [],
        "quantities": {},
        "delivery_window": "",
        "notes": "",
    }
    if request.method == "GET":
        return render_template(
            "harvest.html",
            form_data=form_data,
            crops=HARVEST_CROPS,
            buyer_types=BUYER_TYPES,
        )

    form_data.update({
        "company": request.form.get("company", "").strip(),
        "contact_name": request.form.get("contact_name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "buyer_type": request.form.get("buyer_type", "").strip(),
        "crops": list(dict.fromkeys(request.form.getlist("crops"))),
        "delivery_window": request.form.get("delivery_window", "").strip(),
        "notes": request.form.get("notes", "").strip(),
        "quantities": {},
    })
    errors = validate_contact(
        form_data["contact_name"], form_data["email"], form_data["phone"]
    )
    if (
        not form_data["company"]
        or len(form_data["company"]) > 120
        or any(ord(character) < 32 for character in form_data["company"])
    ):
        errors.append("Enter an organization name (up to 120 characters).")
    if form_data["buyer_type"] not in BUYER_TYPES:
        errors.append("Select your buyer type.")
    if not form_data["crops"] or any(
        crop not in HARVEST_CROPS for crop in form_data["crops"]
    ):
        errors.append("Select at least one listed crop.")
    if form_data["delivery_window"] not in {"0-30", "31-90", "flexible"}:
        errors.append("Select a preferred delivery window.")
    if len(form_data["notes"]) > 2000:
        errors.append("Keep additional notes to 2,000 characters or fewer.")

    quantity_values = {}
    for crop in form_data["crops"]:
        raw_quantity = request.form.get(f"quantity_{crop}", "").strip()
        form_data["quantities"][crop] = raw_quantity
        if not re.fullmatch(r"[0-9]{1,6}(?:\.[0-9])?", raw_quantity):
            quantity = Decimal(0)
        else:
            try:
                quantity = Decimal(raw_quantity)
            except InvalidOperation:
                quantity = Decimal(0)
        if not quantity.is_finite() or quantity <= 0 or quantity > 100000:
            errors.append(f"Enter a valid bulk quantity for {HARVEST_CROPS.get(crop, {}).get('name', 'each selected crop')}.")
        else:
            quantity_values[crop] = quantity.normalize()

    if errors:
        return render_whatsapp_error(
            "harvest.html",
            form_data,
            " ".join(errors),
            crops=HARVEST_CROPS,
            buyer_types=BUYER_TYPES,
        )

    order_lines = [
        f"- {HARVEST_CROPS[crop]['name']}: {format(quantity_values[crop], 'f')} {HARVEST_CROPS[crop]['unit']}"
        for crop in form_data["crops"]
    ]
    delivery_label = {
        "0-30": "Within 30 days",
        "31-90": "31-90 days",
        "flexible": "Flexible",
    }[form_data["delivery_window"]]
    message = (
        "Earth Family Farms - wholesale harvest inquiry\n"
        f"Organization: {' '.join(form_data['company'].split())}\n"
        f"Buyer type: {BUYER_TYPES[form_data['buyer_type']]}\n"
        f"Contact: {form_data['contact_name']}\n"
        f"Email: {form_data['email']}\n"
        f"Phone / WhatsApp: {form_data['phone']}\n"
        f"Requested products:\n{chr(10).join(order_lines)}\n"
        f"Preferred delivery: {delivery_label}\n"
        f"Notes: {' '.join(form_data['notes'].split()) or 'None'}\n"
        "Quantities are inquiry requests and subject to availability."
    )
    return redirect(build_whatsapp_url(message), code=303)


@app.route("/vitals")
def vitals():
    return render_template("vitals.html", vitals=get_vitals_demo())


@app.route("/stays", methods=["GET", "POST"])
def stays():
    if request.method == "GET":
        return render_template(
            "stays.html", form_data={}, today=date.today().isoformat()
        )

    form_data = {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "package": request.form.get("package", "").strip(),
        "date": request.form.get("date", "").strip(),
        "notes": request.form.get("notes", "").strip(),
    }
    errors = []

    if (
        not form_data["name"]
        or len(form_data["name"]) > 100
        or any(ord(character) < 32 for character in form_data["name"])
    ):
        errors.append("Enter your name (up to 100 characters).")
    if len(form_data["email"]) > 254 or not EMAIL_PATTERN.fullmatch(form_data["email"]):
        errors.append("Enter a valid email address.")
    if (
        not PHONE_PATTERN.fullmatch(form_data["phone"])
        or not any(character.isdigit() for character in form_data["phone"])
    ):
        errors.append("Enter a valid phone or WhatsApp number.")
    if form_data["package"] not in BOOKING_PACKAGES:
        errors.append("Select an available stay or experience.")
    if len(form_data["notes"]) > 2000:
        errors.append("Keep your message to 2,000 characters or fewer.")

    preferred_date = parse_booking_date(form_data["date"])
    if form_data["date"] and (preferred_date is None or preferred_date < date.today()):
        errors.append("Choose a valid preferred date that is not in the past.")

    if errors:
        return render_template(
            "stays.html",
            form_data=form_data,
            today=date.today().isoformat(),
            error=" ".join(errors),
        ), 400

    if not resend.api_key or not BOOKING_EMAIL:
        app.logger.error(
            "Booking email could not be sent: RESEND_API_KEY and BOOKING_EMAIL must be configured."
        )
        return render_template(
            "stays.html",
            form_data=form_data,
            today=date.today().isoformat(),
            error="Booking requests are temporarily unavailable. Please contact us on WhatsApp.",
        ), 503

    guest_name = html.escape(form_data["name"])
    guest_email = html.escape(form_data["email"])
    guest_phone = html.escape(form_data["phone"])
    package = html.escape(form_data["package"])
    preferred_date_text = html.escape(form_data["date"] or "Not specified")
    notes = html.escape(form_data["notes"] or "None")
    params = {
        "from": f"Earth Family Farms <{RESEND_FROM_EMAIL}>",
        "to": [BOOKING_EMAIL],
        "reply_to": form_data["email"],
        "subject": f"New Stay Inquiry from {form_data['name']}",
        "html": f"""
            <h2>New Booking Inquiry - Earth Family Farms</h2>
            <p><strong>Name:</strong> {guest_name}</p>
            <p><strong>Email:</strong> {guest_email}</p>
            <p><strong>Phone / WhatsApp:</strong> {guest_phone}</p>
            <p><strong>Selection:</strong> {package}</p>
            <p><strong>Preferred date:</strong> {preferred_date_text}</p>
            <p><strong>Message / group size:</strong><br>{notes}</p>
        """,
    }

    try:
        resend.Emails.send(params)
    except (ResendError, RuntimeError):
        app.logger.exception("Resend dispatch failed for a stay inquiry.")
        return render_template(
            "stays.html",
            form_data=form_data,
            today=date.today().isoformat(),
            error="We could not send your request just now. Please try again or contact us on WhatsApp.",
        ), 503

    return render_template(
        "stays.html", form_data={}, today=date.today().isoformat(), success=True
    )


@app.route("/demo/<villa_slug>", methods=["GET", "POST"])
def custom_demo(villa_slug):
    villa = VILLA_PROSPECTS.get(villa_slug.lower())
    if villa is None:
        abort(404)

    form_data = {
        "guest_name": "",
        "checkin": "",
        "checkout": "",
        "guests": "2 Adults",
        "upsell": villa["upsells"][0],
    }
    if request.method == "GET":
        return render_template(
            "villa_funnel.html",
            villa=villa,
            form_data=form_data,
            today=date.today().isoformat(),
        )

    form_data.update({
        key: request.form.get(key, "").strip()
        for key in ("guest_name", "checkin", "checkout", "guests", "upsell")
    })
    checkin = parse_booking_date(form_data["checkin"])
    checkout = parse_booking_date(form_data["checkout"])
    errors = []

    if (
        not form_data["guest_name"]
        or len(form_data["guest_name"]) > 100
        or any(ord(character) < 32 for character in form_data["guest_name"])
    ):
        errors.append("Enter your name (up to 100 characters).")
    if checkin is None or checkin < date.today():
        errors.append("Choose a valid check-in date that is not in the past.")
    if checkout is None or (checkin and checkout <= checkin):
        errors.append("Check-out must be after check-in.")
    if form_data["guests"] not in GUEST_OPTIONS:
        errors.append("Select a valid guest count.")
    if form_data["upsell"] not in villa["upsells"]:
        errors.append("Select a valid concierge preference.")
    if errors:
        return render_template(
            "villa_funnel.html",
            villa=villa,
            form_data=form_data,
            today=date.today().isoformat(),
            error=" ".join(errors),
        ), 400

    message = (
        f"Hello {villa['name']}! I'd like to request a direct booking:\n\n"
        f"Name: {form_data['guest_name']}\n"
        f"Dates: {checkin.isoformat()} to {checkout.isoformat()}\n"
        f"Guests: {form_data['guests']}\n"
        f"Preference: {form_data['upsell']}\n\n"
        "Are these dates available for direct reservation?"
    )
    whatsapp_url = f"https://wa.me/{villa['whatsapp']}?text={urllib.parse.quote(message)}"
    return render_template(
        "villa_funnel.html",
        villa=villa,
        whatsapp_url=whatsapp_url,
        guest_name=form_data["guest_name"],
    )


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "").lower() == "true")