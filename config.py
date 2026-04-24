# config.py

# When new categories are added in Excel, just add the header name to the list below.

METADATA_FIELDS = [
    "Date", "Location",  "Organization/Individual", "City", "State", "Country",
    "Type of cleanup", "Specify Other (Type of cleanup)", "Type of location", 
    "Distance cleaned", "Units (Distance cleaned)", "Duration (hrs)", 
    "Start time", "End time", "Current Weather", 
    "Wind", "Recent weather", 
    "Tide/Water Level", "Flow Conditions", "Other (Tide/Water Level/Flow Conditions)", "Recent events", "Total weight", "Units (Total weight)",
    "# of participants", "Unusual items", "Notes/comments"
]

DEBRIS_GROUPS = {
    "Plastic": [
        "Plastic drink bottles", "Food wrappers", "Plastic grocery bags", 
        "Plastic bags (Zip-loc, etc)", "Straws/stirrers", "Utensils", 
        "Plastic cups/plates", "Plastic lids", "Plastic take away containers", "Plastic bottle caps", 
        "Cigarettes", "Vaping cartidges/pods", "Cigar tips", 
        "Personal hygiene", "Dental/floss picks", "Tampons/applicators", "Wipes", # Added these
        "Toys", "Balloons", "Lighters", "Shotgun shells/wadding", 
        "Strapping bands", "Zip-ties", "Shipping/packaging", 
        "Plastic sheeting/tape", "Oil/lube bottles", "Bleach/cleaner bottles"
    ],
    "PPE": [
        "Masks (reusable/fabric)", "Masks (disposable)", 
        "Gloves (disposable)", "Hand sanitizer"
    ],
    "Metal": [
        "Cans", "Metals caps/lids", "Batteries", "Metal pieces"
    ],
    "Glass & Rubber": [
        "Glass bottles", "Glass pieces", "Tires", "Rubber pieces"
    ],
    "Paper & Cloth": [
        "Shoes", "Fabric pieces", "Clothing/towels/gloves", "Paper straws", 
        "Paper bags", "Paper cups/plates", "Paper/tissues/napkins", 
        "Paper Shipping/packaging"
    ],
    "Fishing Debris": [
        "Bait containers/crates", "Lobster claw bands", "Fishing nets", 
        "Lures and lightsticks", "Derelict traps/trap pieces", "Buoys/floats", "Rope"
    ],
    "Microplastics & Fibers": [
        "Micro plastic 0-5mm", "SMALL plastic 5-30mm", "LARGE plastic >30mm",
        "Line/net fiber: MICRO 0-5mm", "Line/net fiber: SMALL 5-30mm", 
        "Line/net fiber: LARGE >30mm", "Resin Pellets", "BBs/beads"
    ],
    "Foam": [
        "Foam cups/plates", "Foam take away containers", "Foam Toys",
        "Foam Toys (water/pool)", "Foam Shipping/packaging", "Foam Buoys",
        "Foam Coolers", "Dock Foam (any size)",  "Pink Construction Foam",
         "Blue Construction Foam", "Construction Foam w Foil", 'MICRO foam <5mm',
        "SMALL foam 5-30mm", "LARGE foam >30mm", "Foam Meat Trays"
    ],
    "Other": [
        "Home & garden items", "Car/boat parts", "Other", "Unidentified pieces"
    ]
}

SUMMARY_TOTALS = [
    "Total Plastic", "Total Foam", "Total PPE", "Total Metal", 
    "Total Glass & Rubber", "Total Paper & Cloth", 
    "Total Fishing Debris", "Total Microplastics", "Grand Total", "Outlier"
]


DROPDOWN_OPTIONS = {
    "State": ["N/A","AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
    "Type of cleanup": ["Shoreline (hands)", "Surface (hands)", "Underwater (hands)", "Dip net", "Neuston net", "ROV", "Sediment container", "Sediment grab", "Other"],
    "Type of location": ["Sandy Beach", "Rocky Beach", "Private Dock", "Marina", "Park", "Open Water", "River", "Other"],
    "Current Weather": ["Clear/Sunny", "Rain", "Cloudy", "Windy", "Foggy", "Other"],
    "Wind" : ["Calm (<1 knots / < 1 mph)", "Light Air (1-3 knots / 1-3 mph)", "Light Breeze (4-6 knots / 4-7 mph)", "Gentle Breeze (7-10 knots / 8-12 mph)", "Moderate Breeze (11-16 knots / 13-18 mph)", "Fresh Breeze (17-21 knots / 19-24 mph)", "Strong Breeze (22-27 knots / 25-31 mph)", "Near Gale (28-33 knots / 32-38 mph)", "Gale (34-40 knots / 39-46 mph)", "Strong Gale (41-47 knots / < 47-54 mph)", "Storm (48-55 knots / 55-63 mph)", "Violent Storm (56-63 knots / 64-72 mph)","Hurricane (> 64 knots / >73 mph)"],
    "Recent weather": ["None", "Wind Event", "Rain Event", "Storm Event", "Draught", "Hurricane", "Other"],
    "Tide/Water Level": ["High", "Low", "Mid", "Extreme Low", "Extreme High", "Other", "N/A"],
    "Flow Conditions": ["Ebbing (Tidal)", "Flooding (Tidal)", "Slack (Tidal)", "Flat (Lacustrine)", "Waves (Lacustrine)", "Choppy (Lacustrine)", "White-caps (Lacustrine)", "Stormflow (Riverine)", "Low flow (Riverine)", "Dry bed (Riverine)" ,"Other", "N/A"],
    "Recent events": ["None", "Festival", "Holiday", "Concert", "Busy Weekend", "Summer Camp", "Flood", "Storm", "Hurricane", "Other"],
    "Start time": [
        "12:00 AM", "12:15 AM", "12:30 AM", "12:45 AM", "1:00 AM", "1:15 AM", "1:30 AM", "1:45 AM", "2:00 AM", "2:15 AM", "2:30 AM", "2:45 AM", "3:00 AM", "3:15 AM", "3:30 AM", "3:45 AM", "4:00 AM", "4:15 AM", "4:30 AM", "4:45 AM", "5:00 AM", "5:15 AM", "5:30 AM", "5:45 AM", 
        "6:00 AM", "6:15 AM", "6:30 AM", "7:00 AM", "7:15 AM", "7:30 AM", "7:45 AM", "8:00 AM", "8:15 AM", "8:30 AM", "8:45 AM", "9:00 AM", "9:15 AM", "9:30 AM", "9:45 AM", "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM", "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM",
        "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM", "1:00 PM", "1:15 PM", "1:30 PM", "1:45 PM", "2:00 PM", "2:15 PM", "2:30 PM", "2:45 PM", "3:00 PM", "3:15 PM", "3:30 PM", "3:45 PM", "4:00 PM", "4:15 PM", "4:30 PM", "4:45 PM", "5:00 PM", "5:15 PM", "5:30 PM", "5:45 PM", 
        "6:00 PM", "6:15 PM", "6:30 PM", "7:00 PM", "7:15 PM", "7:30 PM", "7:45 PM", "8:00 PM", "8:15 PM", "8:30 PM", "8:45 PM", "9:00 PM", "9:15 PM", "9:30 PM", "9:45 PM", "10:00 PM", "10:15 PM", "10:30 PM", "10:45 PM", "11:00 PM", "11:15 PM", "11:30 PM", "11:45 PM"
    ],
    "End time": [
        "12:00 AM", "12:15 AM", "12:30 AM", "12:45 AM", "1:00 AM", "1:15 AM", "1:30 AM", "1:45 AM", "2:00 AM", "2:15 AM", "2:30 AM", "2:45 AM", "3:00 AM", "3:15 AM", "3:30 AM", "3:45 AM", "4:00 AM", "4:15 AM", "4:30 AM", "4:45 AM", "5:00 AM", "5:15 AM", "5:30 AM", "5:45 AM", 
        "6:00 AM", "6:15 AM", "6:30 AM", "7:00 AM", "7:15 AM", "7:30 AM", "7:45 AM", "8:00 AM", "8:15 AM", "8:30 AM", "8:45 AM", "9:00 AM", "9:15 AM", "9:30 AM", "9:45 AM", "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM", "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM",
        "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM", "1:00 PM", "1:15 PM", "1:30 PM", "1:45 PM", "2:00 PM", "2:15 PM", "2:30 PM", "2:45 PM", "3:00 PM", "3:15 PM", "3:30 PM", "3:45 PM", "4:00 PM", "4:15 PM", "4:30 PM", "4:45 PM", "5:00 PM", "5:15 PM", "5:30 PM", "5:45 PM", 
        "6:00 PM", "6:15 PM", "6:30 PM", "7:00 PM", "7:15 PM", "7:30 PM", "7:45 PM", "8:00 PM", "8:15 PM", "8:30 PM", "8:45 PM", "9:00 PM", "9:15 PM", "9:30 PM", "9:45 PM", "10:00 PM", "10:15 PM", "10:30 PM", "10:45 PM", "11:00 PM", "11:15 PM", "11:30 PM", "11:45 PM"
    ],
}