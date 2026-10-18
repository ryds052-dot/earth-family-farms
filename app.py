@app.route('/stays')
def stays():
    # Pass accommodation options directly to the template
    accommodations = [
        {
            "name": "Eco-Hostel Bunks",
            "price": "$25 USD",
            "period": "per night",
            "type": "Shared Lodge",
            "description": "Open-air, thoughtfully crafted shared dorm bunks designed for digital nomads, solo travelers, and nature seekers.",
            "features": ["Solar-heated rainwater showers", "Panoramic morning ridge views", "Secure locker storage", "Natural cross-breeze ventilation"]
        },
        {
            "name": "Private Eco-Camping",
            "price": "$10 USD",
            "period": "per night",
            "type": "Terraced Pitch",
            "description": "Pitch your tent under the lush canopy on designated terraced clearings surrounded by native rainforest.",
            "features": ["Access to pure river spring water", "Communal fire pits", "Composting amenities", "Full night-sky canopy views"]
        },
        {
            "name": "Luxury Ridge Suites",
            "price": "Inquire",
            "period": "per night",
            "type": "Private Sanctuary",
            "description": "Private off-grid timber cabins perched along the ridge with floor-to-ceiling wilderness views.",
            "features": ["Private balcony & lounge", "Solar-powered luxury amenities", "Organic farm breakfast included", "Direct spring trail access"]
        }
    ]
    return render_template('stays.html', accommodations=accommodations)