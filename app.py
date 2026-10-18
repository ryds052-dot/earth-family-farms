from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/estates')
def estates():
    return render_template('estates.html')

@app.route('/experiences')
def experiences():
    return render_template('experiences.html')

@app.route('/stays')
def stays():
    accommodations = [
        {
            "name": "Campsite",
            "price": "$20.00 USD",
            "period": "per night",
            "type": "Bring Your Own Tent",
            "description": "Bring your own tent & linen to set up on designated terraced grounds surrounded by nature.",
            "features": [
                "Terraced campsite access",
                "Shared outdoor facilities",
                "Pure mineral river spring access",
                "Scenic natural surroundings"
            ]
        },
        {
            "name": "Dorm Bunks",
            "price": "$30.00 USD",
            "period": "per night",
            "type": "Shared Lodge",
            "description": "Handcrafted wooden bunk beds inside comfortable shared lodging with natural ventilation.",
            "features": [
                "Bunk beds with comfortable bedding",
                "Shared eco-facilities & showers",
                "Panoramic ridge & rainforest views",
                "Tranquil atmosphere for solo travelers"
            ]
        },
        {
            "name": "Dorm Tent",
            "price": "$30.00 USD",
            "period": "per night",
            "type": "Enclosed Setup",
            "description": "Enclosed, pre-setup tent area with shared facilities. Additional guests at $10 per person.",
            "features": [
                "Pre-pitched enclosed dome tent",
                "Shared eco-facilities",
                "Additional $10 USD/person (flexible group setup)",
                "Full outdoor immersion"
            ]
        },
        {
            "name": "Queen Cabin",
            "price": "$55.00 USD",
            "period": "per night (double occupancy)",
            "type": "Private Cabin",
            "description": "Private, rustic wooden cabin with a plush queen bed. Additional $10 per person (up to 4 max).",
            "features": [
                "Private wooden cabin retreat",
                "Shared facilities (2 guests included)",
                "Expandable up to 4 guests max",
                "Private balcony overlooking the sanctuary"
            ]
        }
    ]
    return render_template('stays.html', accommodations=accommodations)

@app.route('/api/inquire', methods=['POST'])
def handle_inquiry():
    data = request.get_json() or {}
    name = data.get('name', 'Valued Guest')
    email = data.get('email', '')
    stay_type = data.get('stay_type', 'General Stay')
    message = data.get('message', '')
    
    print(f"[INQUIRY RECEIVED] Name: {name} | Email: {email} | Type: {stay_type} | Message: {message}")
    
    return jsonify({
        "status": "success",
        "message": f"Thank you {name}, your inquiry for {stay_type} has been received! We will reach out shortly."
    })

if __name__ == '__main__':
    app.run(debug=True)