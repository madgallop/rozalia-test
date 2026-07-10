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

ALL_COLUMNS = METADATA_FIELDS + [item for sublist in DEBRIS_GROUPS.values() for item in sublist] + SUMMARY_TOTALS