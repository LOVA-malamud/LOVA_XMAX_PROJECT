import sqlite3

def setup_scooter_db():
    # יצירת חיבור לבסיס הנתונים (יוצר קובץ חדש אם לא קיים)
    conn = sqlite3.connect('xmax_specs.db')
    cursor = conn.cursor()

    # 1. יצירת טבלה למפרט טכני כללי
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bike_specs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            parameter TEXT,
            value TEXT
        )
    ''')

    # מידע שנאסף על ה-XMAX 400 2020 שלך
    specs_data = [
        ('Engine', 'Type', '395cc, Liquid-cooled, 4-stroke, Single cylinder, DOHC'),
        ('Engine', 'Maximum Power', '24.5 kW (32.9 HP) @ 7,000 rpm'),
        ('Engine', 'Maximum Torque', '36.0 Nm @ 6,000 rpm'),
        ('Engine', 'Compression Ratio', '10.6 : 1'),
        ('Fluids', 'Engine Oil Capacity', '1.5L (1.7L with filter replacement)'),
        ('Fluids', 'Gear Oil Capacity', '0.25L'),
        ('Maintenance', 'Valve Clearance (Intake)', '0.08–0.12 mm'),
        ('Maintenance', 'Valve Clearance (Exhaust)', '0.16–0.20 mm'),
        ('Maintenance', 'Oil Change Interval', 'Every 5,000 km'),
        ('Maintenance', 'V-Belt Replacement', 'Every 10,000 - 20,000 km'),
        ('Chassis', 'Front Tire', '120/70-15'),
        ('Chassis', 'Rear Tire', '150/70-13'),
        ('Chassis', 'Front Tire Pressure', '32 PSI'),
        ('Chassis', 'Rear Tire Pressure', '36 PSI'),
        ('Electrical', 'Battery Type', 'GTZ8V'),
        ('Dimensions', 'Wet Weight', '210 kg'),
        ('Dimensions', 'Fuel Tank Capacity', '13 Liters')
    ]

    # הכנסת הנתונים בצורה בטוחה (Parameterized Query)
    cursor.executemany('INSERT INTO bike_specs (category, parameter, value) VALUES (?, ?, ?)', specs_data)

    # שמירה וסגירה
    conn.commit()
    print("Database created and populated successfully!")
    return conn

def query_specs(conn):
    cursor = conn.cursor()
    print("\n--- Technical Specifications for Yamaha XMAX 400 2020 ---")
    
    # שליפת כל המידע מה-DB
    cursor.execute('SELECT category, parameter, value FROM bike_specs')
    rows = cursor.fetchall()

    for row in rows:
        print(f"[{row[0]}] {row[1]}: {row[2]}")

# הרצה
if __name__ == "__main__":
    db_connection = setup_scooter_db()
    query_specs(db_connection)
    db_connection.close()
