import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import resend

app = Flask(__name__)

# Configure SQLite Database (or your existing database URI)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///farms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure Resend API Key from environment variables
resend.api_key = os.getenv('RESEND_API_KEY')

# Define your Database Model for Bookings
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    service = db.Column(db.String(100), nullable=False)

# Create database tables automatically if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    phone = request.form.get('phone')
    service = request.form.get('service')
    
    # 1. Save the booking into your SQLAlchemy database
    try:
        new_booking = Booking(name=name, phone=phone, service=service)
        db.session.add(new_booking)
        db.session.commit()
    except Exception as e:
        print(f"Database error: {e}")

    # 2. Send an instant email notification via Resend
    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev", # Replace with your verified domain email if applicable
            "to": "ryds052@gmail.com",       # Your personal email for instant alerts
            "subject": f"🚀 New Booking: {service}",
            "html": f"<h3>New Lead Received</h3><p><b>Name:</b> {name}</p><p><b>Phone:</b> {phone}</p><p><b>Service:</b> {service}</p>"
        })
    except Exception as e:
        print(f"Resend email error: {e}")
    
    # 3. Redirect them to a clean success screen (or a WhatsApp redirect to your phone)
    # If you want it to bounce straight to a WhatsApp chat with you, use this format:
    whatsapp_message = f"Hello, I just booked {service} on your site. My name is {name}."
    # Replace with your actual WhatsApp phone number format (country code + number, e.g., 1876xxxxxxx)
    my_phone_number = "18765555555" 
    
    return render_template('success.html', name=name, service=service, phone=phone)

if __name__ == '__main__':
    app.run(debug=True)