# config.py

METADATA_FIELDS = [
    "Date", 
    "Submission Timestamp", 
    "Location", 
    "Name of Organization/Individual", 
    "Email", 
    "City", 
    "State", 
    "Country",
    "Type of cleanup", 
    "Type of location (i.e. Sandy Beach, Marina, Open Water)", 
    "Distance cleaned", 
    "Units (Distance cleaned)", 
    "Duration (hrs)", 
    "Start time",
    "Total weight", 
    "Units (Total weight)", 
    "# of participants", 
    "Unusual items", 
    "Notes/comments"
]

DEBRIS_GROUPS = {
    "Plastic": [
        "Plastic drink bottles", "Food wrappers", "Plastic grocery bags", 
        "Plastic bags (Zip-loc, etc)", "Straws/stirrers", "Utensils", 
        "Plastic cups/plates", "Plastic lids", "Plastic take away containers", "Plastic bottle caps", 
        "Cigarettes", "Vaping cartidges/pods", "Cigar tips", 
        "Personal hygiene", "Dental/floss picks", "Tampons/applicators", "Wipes", 
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
        "Foam Coolers", "Dock Foam (any size)", "Pink Construction Foam",
        "Blue Construction Foam", "Construction Foam w Foil", "MICRO foam <5mm", 
        "SMALL foam 5-30mm", "LARGE foam >30mm", "Foam Meat Trays"
    ],
    "Miscellaneous": [
        "Needles", "Home & garden items", "Car/boat parts", "Other", "Unidentified pieces"
    ]
}

SUMMARY_TOTALS = [
    "Total Plastic Items (excluding Foam)", 
    "Total Foam Items", 
    "Total PPE Items", 
    "Total Metal Items", 
    "Total Glass/Rubber Items", 
    "Total Paper/Cloth Items", 
    "Total Fishing Debris Items", 
    "Total Plastic Fragments (> 30mm)", 
    "Total Plastic Fragments (5-30mm)", 
    "Total Microplastics (0-5mm)", 
    "Total Misc", 
    "Total (All)", 
    "Outlier"
]

DROPDOWN_OPTIONS = {
    "State": ["N/A","AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
    "Type of cleanup": ["Beach/Shoreline", "Underwater", "Water Surface"],
    "Start time": [
        "12:00 AM", "12:15 AM", "12:30 AM", "12:45 AM", "1:00 AM", "1:15 AM", "1:30 AM", "1:45 AM", "2:00 AM", "2:15 AM", "2:30 AM", "2:45 AM", "3:00 AM", "3:15 AM", "3:30 AM", "3:45 AM", "4:00 AM", "4:15 AM", "4:30 AM", "4:45 AM", "5:00 AM", "5:15 AM", "5:30 AM", "5:45 AM", 
        "6:00 AM", "6:15 AM", "6:45 AM", "6:30 AM", "7:00 AM", "7:15 AM", "7:30 AM", "7:45 AM", "8:00 AM", "8:15 AM", "8:30 AM", "8:45 AM", "9:00 AM", "9:15 AM", "9:30 AM", "9:45 AM", "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM", "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM",
        "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM", "1:00 PM", "1:15 PM", "1:30 PM", "1:45 PM", "2:00 PM", "2:15 PM", "2:30 PM", "2:45 PM", "3:00 PM", "3:15 PM", "3:30 PM", "3:45 PM", "4:00 PM", "4:15 PM", "4:30 PM", "4:45 PM", "5:00 PM", "5:15 PM", "5:30 PM", "5:45 PM", 
        "6:00 PM", "6:15 PM", "6:30 PM", "6:45 PM", "7:00 PM", "7:15 PM", "7:30 PM", "7:45 PM", "8:00 PM", "8:15 PM", "8:30 PM", "8:45 PM", "9:00 PM", "9:15 PM", "9:30 PM", "9:45 PM", "10:00 PM", "10:15 PM", "10:30 PM", "10:45 PM", "11:00 PM", "11:15 PM", "11:30 PM", "11:45 PM"
    ]
}

ALL_COLUMNS = METADATA_FIELDS + [item for sublist in DEBRIS_GROUPS.values() for item in sublist] + SUMMARY_TOTALS