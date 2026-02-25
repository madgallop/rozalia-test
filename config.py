# config.py

# When new categories are added in Excel, just add the header name to the list below.

METADATA_FIELDS = [
    "Date", "Location", "City", "State", 
    "Type of cleanup", "Type of location", 
    "Distance cleaned (miles)", "Duration (hrs)", 
    "Start time", "End time", "Weather", 
    "Wind (knots)", "Recent weather", 
    "Tide", "Flow", "Recent events", "Total weight (lb)",
    "# of participants", "Unusual items", "Notes/comments", "Outlier"
]

DEBRIS_GROUPS = {
    "Plastic": [
        "Plastic drink bottles", "Food wrappers", "Plastic grocery bags", 
        "Plastic bags (Zip-loc, etc)", "Straws/stirrers", "Utensils", 
        "Plastic cups/plates", "Plastic take away containers", "Plastic bottle caps", 
        "Plastic lids", "Cigarettes", "Vaping cartidges/pods", "Cigar tips", 
        "Personal hygiene", "Dental/floss picks", "Tampons/applicators", "Wipes", # Added these
        "Toys", "Balloons", "Lighters", "Shotgun shells/wadding", 
        "Strapping bands", "Zip-ties", "Shipping/packaging", 
        "Plastic sheeting/tape", "Oil/lube bottles", "Bleach/cleaner bottles"
    ],
    "Foam": [
        "Foam cups/plates", "Foam take away containers", "Micro foam 0-5mm", 
        "SMALL foam 5-30mm", "LARGE foam >30mm", "Dock Foam (any size)", "Foam Toys",
        "Foam Toys (water/pool)", "Foam Shipping/packaging", "Foam Buoys", "Foam Coolers",
        "Pink Construction Foam", "Blue Construction Foam", "Construction Foam w Foil",	"Foam Meat Trays"
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
    "Other": [
        "Home & garden items", "Car/boat parts", "Other", "Unidentified pieces"
    ]
}

SUMMARY_TOTALS = [
    "Total Plastic", "Total Foam", "Total PPE", "Total Metal", 
    "Total Glass & Rubber", "Total Paper & Cloth", 
    "Total Fishing Debris", "Total Microplastics", "Grand Total"
]

DROPDOWN_OPTIONS = {
    "State": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "Can", "Other"],
    "Type of cleanup": ["Shoreline (hands)", "Surface (hands)", "Underwater (hands)", "Dip net", "Neuston net", "ROV", "Sediment container", "Sediment grab", "Other"],
    "Type of location": ["Sandy Beach", "Rocky Beach", "Private Dock", "Marina", "Park", "Open Water", "River", "Other"],
    "Weather": ["Clear/Sunny", "Rain", "Cloudy", "Windy", "Foggy", "Other"],
    "Recent weather": ["Wind Event", "Rain Event", "Storm Event", "Draught", "None", "Irene", "Other"],
    "Tide": ["High", "Low", "Mid", "Other", "N/A"],
    "Flow": ["Ebbing", "Flooding", "Slack", "Other", "N/A"],
    "Recent events": ["Festival", "Holiday", "Concert", "Busy Weekend", "Summer Camp", "None", "Other"],
    "Start time": [
        "12:00 AM", "12:30 AM", "1:00 AM", "1:30 AM", "2:00 AM", "2:30 AM", "3:00 AM", "3:30 AM", "4:00 AM", "4:30 AM", "5:00 AM", "5:30 AM", "6:00 AM", "6:30 AM", "7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
        "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM", "9:30 PM", "10:00 PM", "10:30 PM", "11:00 PM", "11:30 PM"
    ],
    "End time": [
        "12:00 AM", "12:30 AM", "1:00 AM", "1:30 AM", "2:00 AM", "2:30 AM", "3:00 AM", "3:30 AM", "4:00 AM", "4:30 AM", "5:00 AM", "5:30 AM", "6:00 AM", "6:30 AM", "7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
        "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM", "8:00 PM", "8:30 PM", "9:00 PM", "9:30 PM", "10:00 PM", "10:30 PM", "11:00 PM", "11:30 PM"
    ]
}