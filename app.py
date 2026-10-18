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
    # Structured accommodation options passed directly to the template
    accommodations = [
        {
            "name": "Eco-Hostel Bunks",
            "price": "$25 USD",
            "period": "night",
            "type": "Shared Lodge",
            "description": "Open-air, thoughtfully crafted shared dorm bunks designed for digital nomads, solo travelers, and nature seekers in the Ocho Rios highlands.",
            "features": [
                "Solar-heated rainwater showers",
                "Panoramic morning ridge views",
                "Secure locker storage",
                "Natural cross-breeze ventilation",
                "Direct access to river springs"
            ]
        },
        {
            "name": "Private Eco-Camping",
            "price": "$10 USD",
            "period": "night",
            "type": "Terraced Pitch",
            "description": "Pitch your tent under the rainforest canopy on designated terraced clearings surrounded by native flora and pristine wilderness.",
            "features": [
                "Access to pure mineral spring water",
                "Communal fire pits & outdoor sinks",
                "Composting & eco-toilet facilities",
                "Full night-sky canopy views",
                "Complimentary river trail access"
            ]
        },
        {
            "name": "Luxury Ridge Suites",
            "price": "Inquire",
            "period": "custom stay",
            "type": "Private Sanctuary",
            "description": "Private, high-end off-grid cabins perched along the ridge, constructed with sustainably sourced local timber and floor-to-ceiling wilderness glass.",
            "features": [
                "Private balcony & lounge area",
                "Solar-powered luxury amenities",
                "Daily organic farm breakfast included",
                "Private plunge pool access",
                "Highland solitude & sunset ocean views"
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
    
    # Process inquiry (e.g. log, store, or email)
    print(f"[INQUIRY RECEIVED] Name: {name} | Email: {email} | Type: {stay_type} | Message: {message}")
    
    return jsonify({
        "status": "success",
        "message": f"Thank you {name}, your reservation inquiry for {stay_type} has been received! Our team will reach out shortly."
    })

if __name__ == '__main__':
    app.run(debug=True)