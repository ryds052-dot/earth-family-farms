import os
from flask import Flask, render_template, request, flash, redirect, url_for
import resend
import urllib.parse

app = Flask(__name__)
# --- PASTE THIS NEAR THE TOP ---
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

# --- YOUR EXISTING EARTH FAMILY FARMS ROUTES STAY HERE ---
# @app.route('/') ... etc.


# --- PASTE THIS NEW ROUTE ABOVE if __name__ == '__main__': ---
@app.route('/demo/<villa_slug>', methods=['GET', 'POST'])
def custom_demo(villa_slug):
    # Grabs the right villa, or defaults to Upful Villa if you type a random name
    villa = VILLA_PROSPECTS.get(villa_slug.lower(), VILLA_PROSPECTS["upful"])
    
    if request.method == 'POST':
        guest_name = request.form.get('guest_name')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        guests = request.form.get('guests')
        upsell = request.form.get('upsell')
        
        # Build an automatic WhatsApp message with all their choices
        msg = (
            f"Hello {villa['name']}! I'd like to request a direct booking:\n\n"
            f"👤 *Name:* {guest_name}\n"
            f"📅 *Dates:* {checkin} to {checkout}\n"
            f"👥 *Guests:* {guests}\n"
            f"✨ *Preference:* {upsell}\n\n"
            f"Are these dates available for direct reservation?"
        )
        encoded_msg = urllib.parse.quote(msg)
        whatsapp_url = f"https://wa.me/{villa['whatsapp']}?text={encoded_msg}"
        
        return render_template('villa_funnel.html', villa=villa, whatsapp_url=whatsapp_url, guest_name=guest_name)
        
    return render_template('villa_funnel.html', villa=villa)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
app.secret_key = 'earth-family-farms-secret-key'

# Read Environment Variables from Render
resend.api_key = os.environ.get('RESEND_API_KEY')
BOOKING_EMAIL = os.environ.get('BOOKING_EMAIL', 'ryds052@gmail.com')
RESEND_FROM_EMAIL = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/experiences')
def experiences():
    return render_template('experiences.html')

@app.route('/estates')
def estates():
    return render_template('estates.html')

@app.route('/stays', methods=['GET', 'POST'])
def stays():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        stay_type = request.form.get('stay_type', 'General Inquiry')
        message = request.form.get('message')

        try:
            params = {
                "from": f"Earth Family Farms <{RESEND_FROM_EMAIL}>",
                "to": [BOOKING_EMAIL],
                "subject": f"🌿 New Stay Inquiry from {name}",
                "html": f"""
                <h2>New Booking Inquiry - Earth Family Farms</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Phone / WhatsApp:</strong> {phone}</p>
                <p><strong>Selection:</strong> {stay_type}</p>
                <p><strong>Message / Dates:</strong> {message}</p>
                """
            }

            email_response = resend.Emails.send(params)
            print(f"Resend Dispatch Success: {email_response}")
            return render_template('stays.html', success=True)

        except Exception as e:
            print(f"Resend Dispatch Error: {e}")
            return render_template('stays.html', error=True)

    return render_template('stays.html')

if __name__ == '__main__':
    app.run(debug=True)