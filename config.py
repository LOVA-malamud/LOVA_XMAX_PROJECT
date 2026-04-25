import os

# --- APP CONFIGURATION ---
APP_TITLE = "XMAX 400 Tech Max Manager"
APP_ICON = "🛵"

# --- DIRECTORY CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "scooter_db.json")
DB_PATH = os.path.join(SCRIPT_DIR, "xmax_docs.docs", "xmax_parts_database.db")
SCHEMATICS_DIR = os.path.join(SCRIPT_DIR, "schematics")
DOCS_DIR = os.path.join(SCRIPT_DIR, "xmax_docs.docs")

# --- AI CONFIGURATION ---
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_MAX_RETRIES = 3

AI_STOP_WORDS = [
    'which', 'what', 'is', 'the', 'i', 'need', 'for', 'a', 'can', 'you',
    'show', 'me', 'part', 'number', 'my', 'scooter', 'yamaha', 'xmax',
    'please', 'help', 'do', 'does', 'want', 'to', 'replace', 'broken', 'new',
]

# --- MAINTENANCE CONFIG ---
MAINTENANCE_INTERVALS = {
    "Engine Oil (10W40)":   {"interval": 5000,  "keywords": ["oil", "שמן", "טיפול"],                          "predictive": False},
    "Oil Filter":           {"interval": 10000, "keywords": ["oil filter", "פילטר שמן", "מסנן שמן"],           "predictive": False},
    "Air Filters":          {"interval": 10000, "keywords": ["air filter", "פילטר אוויר", "מסנן אוויר"],       "predictive": True},
    "V-Belt":               {"interval": 20000, "keywords": ["belt", "רצועה", "ווריאטור", "וריאטור"],           "predictive": True},
    "Spark Plug (NGK CR7E)":{"interval": 20000, "keywords": ["plug", "פלאג", "מצת"],                           "predictive": False},
    "Transmission Oil":     {"interval": 10000, "keywords": ["transmission", "גיר", "שמן גיר"],                "predictive": False},
    "Variator Weights":     {"interval": 10000, "keywords": ["weights", "משקולות", "רולרים"],                   "predictive": False},
    "Brake Fluid (DOT 4)":  {"interval": 20000, "keywords": ["brake fluid", "נוזל בלם", "ברקס"],               "predictive": False},
    "Coolant":              {"interval": 30000, "keywords": ["coolant", "נוזל קירור", "מים לרדיאטור"],          "predictive": False},
}

# --- COST CATEGORIZATION ---
COST_CATEGORY_KEYWORDS = [
    "filter", "plug", "belt", "weights", "fluid", "part", "tyre",
    "tire", "brake", "oil", "coolant", "battery", "spark", "roller",
]

# --- TECH SPECS SEED DATA (source of truth for DB seeding) ---
TECH_SPECS_SEED = [
    ('Engine', 'Displacement', '395', 'cc'),
    ('Engine', 'Bore x Stroke', '83.0 x 73.0', 'mm'),
    ('Engine', 'Compression Ratio', '10.6:1', None),
    ('Engine', 'Max Power', '24.5', 'kW @ 7000 rpm'),
    ('Engine', 'Max Torque', '36.0', 'Nm @ 6000 rpm'),
    ('Engine', 'Idle Speed', '1300-1500', 'rpm'),
    ('Valves', 'Exhaust Clearance', '0.25 - 0.30', 'mm'),
    ('Valves', 'Intake Clearance', '0.15 - 0.20', 'mm'),
    ('Fluids', 'Coolant Total', '1.4', 'L'),
    ('Fluids', 'Engine Oil (Periodic)', '1.5', 'L'),
    ('Fluids', 'Engine Oil (With Filter)', '1.7', 'L'),
    ('Fluids', 'Fuel Tank', '13', 'L'),
    ('Fluids', 'Transmission Oil', '0.25', 'L'),
    ('Tires', 'Front Pressure (Cold)', '2.25', 'bar (33 psi)'),
    ('Tires', 'Rear Pressure (Cold)', '2.50', 'bar (36 psi)'),
    ('Electrical', 'Battery', 'GTZ10S', '12V, 8.6 Ah'),
    ('Electrical', 'Spark Plug', 'NGK CR7E', None),
    ('Electrical', 'Spark Plug Gap', '0.7 - 0.8', 'mm'),
    ('Torque', 'Front Axle Nut', '52', 'Nm'),
    ('Torque', 'Oil Drain Bolt', '20', 'Nm'),
    ('Torque', 'Oil Filter Cover', '10', 'Nm'),
    ('Torque', 'Rear Axle Nut', '135', 'Nm'),
    ('Torque', 'Spark Plug', '13', 'Nm'),
    ('Intervals', 'Air Filter', '10000', 'km'),
    ('Intervals', 'Engine Oil', '5000', 'km'),
    ('Intervals', 'V-Belt', '20000', 'km'),
]
