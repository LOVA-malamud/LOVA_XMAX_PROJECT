import os

# --- APP CONFIGURATION ---
APP_TITLE = "XMAX 400 Tech Max Manager"
APP_ICON = "🛵"

# --- DIRECTORY CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "scooter_db.json")  # Legacy support during migration
DB_PATH = os.path.join(SCRIPT_DIR, "xmax_docs.docs", "xmax_parts_database.db")
SCHEMATICS_DIR = os.path.join(SCRIPT_DIR, "schematics")
DOCS_DIR = os.path.join(SCRIPT_DIR, "xmax_docs.docs")

# --- MAINTENANCE CONFIG ---
MAINTENANCE_INTERVALS = {
    "Engine Oil (10W40)": {"interval": 5000, "keywords": ["oil", "שמן", "טיפול"]},
    "Oil Filter": {"interval": 10000, "keywords": ["oil filter", "פילטר שמן", "מסנן שמן"]},
    "Air Filters": {"interval": 10000, "keywords": ["air filter", "פילטר אוויר", "מסנן אוויר"]},
    "V-Belt": {"interval": 20000, "keywords": ["belt", "רצועה", "ווריאטור", "וריאטור"]},
    "Spark Plug (NGK CR7E)": {"interval": 20000, "keywords": ["plug", "פלאג", "מצת"]},
    "Transmission Oil": {"interval": 10000, "keywords": ["transmission", "גיר", "שמן גיר"]},
    "Variator Weights": {"interval": 10000, "keywords": ["weights", "משקולות", "רולרים"]},
    "Brake Fluid (DOT 4)": {"interval": 20000, "keywords": ["brake fluid", "נוזל בלם", "ברקס"]},
    "Coolant": {"interval": 30000, "keywords": ["coolant", "נוזל קירור", "מים לרדיאטור"]}
}

TECH_SPECS = {
    "Oils & Fluids": [
        ("Engine Oil (Standard)", "1.5 L"),
        ("Engine Oil (With Filter)", "1.7 L"),
        ("Oil Type", "10W-40 (JASO MA/MB)"),
        ("Transmission Oil", "0.25 L"),
        ("Coolant", "1.1 L"),
        ("Fuel Tank", "13 L")
    ],
    "Tires & Chassis": [
        ("Front Tire Pressure", "33 PSI"),
        ("Rear Tire Pressure", "36 PSI"),
        ("Brake Fluid", "DOT 4"),
        ("Battery", "12V, 7.4 Ah (GTZ8V)"),
        ("Wet Weight", "210 kg")
    ],
    "Essential Tools": [
        ("Rear Axle Nut", "19 mm"),
        ("Exhaust/Swingarm", "14 mm / 12 mm"),
        ("Spark Plug Socket", "16 mm Deep"),
        ("Oil Drain Bolt Torque", "20 Nm")
    ]
}
