import os
from flask import Flask, render_template, request, flash, redirect, url_for
import resend

app = Flask(__name__)
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