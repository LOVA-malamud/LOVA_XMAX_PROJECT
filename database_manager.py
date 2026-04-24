import sqlite3
import pandas as pd
import json
import os
from datetime import date

class ScooterDB:
    def __init__(self, db_path, data_file):
        self.db_path = db_path
        self.data_file = data_file
        self.init_db()
        self.seed_tech_specs()
        self.seed_custom_rules()
        self.migrate_if_needed()

    def _get_connection(self):
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def init_db(self):
        """Initializes the database and creates tables if they don't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Parts Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS parts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Part_Number TEXT,
                        Description TEXT,
                        Category TEXT,
                        Price_Euro REAL,
                        Image_URL TEXT
                    )
                ''')
                
                # 2. Vehicle Stats Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS vehicle_stats (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                
                # 3. Maintenance History Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS maintenance_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        task TEXT,
                        km INTEGER,
                        cost REAL,
                        notes TEXT
                    )
                ''')

                # 4. Technical Specifications Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tech_specs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        spec_name TEXT NOT NULL,
                        spec_value TEXT NOT NULL,
                        unit TEXT
                    )
                ''')

                # 5. Fuel Logs Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fuel_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        km INTEGER NOT NULL,
                        liters REAL NOT NULL,
                        price REAL
                    )
                ''')

                # 6. Todo / Pending Repairs Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS todo_list (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT NOT NULL,
                        priority TEXT DEFAULT 'Medium',
                        status TEXT DEFAULT 'Pending',
                        added_date TEXT NOT NULL
                    )
                ''')

                # 7. Custom Mechanic Rules Table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS custom_mechanic_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rule_text TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")

    # --- CUSTOM RULES ---
    def get_custom_mechanic_rules(self):
        """Retrieves all custom mechanic rules from the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT rule_text FROM custom_mechanic_rules")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving custom rules: {e}")
            return []

    def add_custom_mechanic_rule(self, rule_text):
        """Adds a new custom mechanic rule."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO custom_mechanic_rules (rule_text) VALUES (?)", (rule_text,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding custom rule: {e}")

    # --- TODO / REPAIRS ---
    def add_todo_item(self, task, priority):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO todo_list (task, priority, added_date)
                    VALUES (?, ?, ?)
                ''', (task, priority, str(date.today())))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding todo item: {e}")

    def get_todo_list(self):
        try:
            with self._get_connection() as conn:
                query = "SELECT id, task, priority, status, added_date FROM todo_list WHERE status = 'Pending' ORDER BY priority DESC"
                return pd.read_sql(query, conn)
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving todo list: {e}")
            return pd.DataFrame()

    def complete_todo_item(self, item_id):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE todo_list SET status = 'Completed' WHERE id = ?", (item_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error completing todo item: {e}")

    # --- FUEL LOGS ---
    def add_fuel_log(self, date_str, km, liters, price):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO fuel_logs (date, km, liters, price)
                    VALUES (?, ?, ?, ?)
                ''', (date_str, km, liters, price))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding fuel log: {e}")

    def get_fuel_history(self):
        try:
            with self._get_connection() as conn:
                query = "SELECT date, km, liters, price FROM fuel_logs ORDER BY date ASC"
                df = pd.read_sql(query, conn)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df['km_diff'] = df['km'].diff()
                    df['l_100km'] = (df['liters'] / df['km_diff']) * 100
                return df
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving fuel history: {e}")
            return pd.DataFrame()

    def seed_tech_specs(self):
        """Seeds the tech_specs table with researched 2020 XMAX 400 data."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tech_specs")
                if cursor.fetchone()[0] > 0:
                    return

                specs = [
                    ('Engine', 'Displacement', '395', 'cc'),
                    ('Engine', 'Bore x Stroke', '83.0 x 73.0', 'mm'),
                    ('Engine', 'Compression Ratio', '10.6:1', None),
                    ('Engine', 'Max Power', '24.5', 'kW @ 7000 rpm'),
                    ('Engine', 'Max Torque', '36.0', 'Nm @ 6000 rpm'),
                    ('Engine', 'Idle Speed', '1300-1500', 'rpm'),
                    ('Valves', 'Intake Clearance', '0.15 - 0.20', 'mm'),
                    ('Valves', 'Exhaust Clearance', '0.25 - 0.30', 'mm'),
                    ('Fluids', 'Engine Oil (Periodic)', '1.5', 'L'),
                    ('Fluids', 'Engine Oil (With Filter)', '1.7', 'L'),
                    ('Fluids', 'Transmission Oil', '0.25', 'L'),
                    ('Fluids', 'Coolant Total', '1.4', 'L'),
                    ('Tires', 'Front Pressure (Cold)', '2.25', 'bar (33 psi)'),
                    ('Tires', 'Rear Pressure (Cold)', '2.50', 'bar (36 psi)'),
                    ('Electrical', 'Spark Plug', 'NGK CR7E', None),
                    ('Electrical', 'Spark Plug Gap', '0.7 - 0.8', 'mm'),
                    ('Electrical', 'Battery', 'GTZ10S', '12V, 8.6 Ah'),
                    ('Torque', 'Spark Plug', '13', 'Nm'),
                    ('Torque', 'Oil Drain Bolt', '20', 'Nm'),
                    ('Torque', 'Oil Filter Cover', '10', 'Nm'),
                    ('Torque', 'Front Axle Nut', '52', 'Nm'),
                    ('Torque', 'Rear Axle Nut', '135', 'Nm'),
                    ('Intervals', 'Engine Oil', '5000', 'km'),
                    ('Intervals', 'V-Belt', '20000', 'km'),
                    ('Intervals', 'Air Filter', '10000', 'km')
                ]
                
                cursor.executemany('''
                    INSERT INTO tech_specs (category, spec_name, spec_value, unit)
                    VALUES (?, ?, ?, ?)
                ''', specs)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error seeding tech specs: {e}")

    def get_tech_specs(self):
        """Fetches all technical specifications and returns them structured by category."""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT category, spec_name, spec_value, unit FROM tech_specs ORDER BY category, spec_name")
                rows = cursor.fetchall()

            if not rows:
                return {"status": "error", "message": "No technical specifications found."}

            structured_data = {}
            for row in rows:
                cat = row['category']
                if cat not in structured_data:
                    structured_data[cat] = []
                
                structured_data[cat].append({
                    "name": row['spec_name'],
                    "value": row['spec_value'],
                    "unit": row['unit']
                })

            return {"status": "success", "data": structured_data}

        except sqlite3.Error as e:
            return {"status": "error", "message": f"Database error: {str(e)}"}

    def migrate_if_needed(self):
        """Migrates data from scooter_db.json to SQLite if the JSON file exists."""
        if os.path.exists(self.data_file):
            print(f"Migrating data from {self.data_file}...")
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update Mileage
                self.update_mileage(data.get('mileage', 0))
                
                # Update History
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM maintenance_history")
                    if cursor.fetchone()[0] == 0:
                        for entry in data.get('history', []):
                            cursor.execute('''
                                INSERT INTO maintenance_history (date, task, km, cost, notes)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (entry['date'], entry['task'], entry['km'], entry['cost'], entry['notes']))
                    conn.commit()
                
                # Rename JSON file to mark migration as done
                os.rename(self.data_file, self.data_file + ".bak")
                print("Migration completed successfully.")
            except Exception as e:
                print(f"Error during migration: {e}")

    # --- MILEAGE ---
    def get_mileage(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM vehicle_stats WHERE key = 'mileage'")
                row = cursor.fetchone()
                return int(row[0]) if row else 0
        except sqlite3.Error as e:
            print(f"Error retrieving mileage: {e}")
            return 0

    def update_mileage(self, new_km):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO vehicle_stats (key, value) VALUES ('mileage', ?)", (str(new_km),))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating mileage: {e}")

    # --- HISTORY ---
    def get_history(self):
        try:
            with self._get_connection() as conn:
                query = "SELECT date, task, km, cost, notes FROM maintenance_history ORDER BY date DESC, km DESC"
                df = pd.read_sql(query, conn)
                return df.to_dict('records')
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving history: {e}")
            return []

    def get_last_service_km(self, keywords):
        """Optimized SQLite query to find the last service KM directly in the database."""
        if not keywords:
            return 0
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                conditions = " OR ".join(["task LIKE ?" for _ in keywords])
                params = [f"%{kw}%" for kw in keywords]
                query = f"SELECT MAX(km) FROM maintenance_history WHERE {conditions}"
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result and result[0] is not None else 0
        except sqlite3.Error as e:
            print(f"Error retrieving last service KM: {e}")
            return 0

    def add_service_log(self, date_str, task, km, cost, notes):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO maintenance_history (date, task, km, cost, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (date_str, task, km, cost, notes))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding service log: {e}")

    # --- UTILITIES ---
    def calculate_usage_stats(self):
        """Calculates average daily mileage based on history."""
        try:
            history = self.get_history()
            if not history or len(history) < 2:
                return None
            
            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            first_date = df['date'].min()
            days_diff = (pd.Timestamp.now() - first_date).days
            
            if days_diff <= 0: return None
            
            total_km_tracked = self.get_mileage() - df['km'].min()
            avg_km_day = total_km_tracked / days_diff
            
            return {
                "avg_km_day": avg_km_day,
                "avg_km_month": avg_km_day * 30.44,
                "days_tracked": days_diff
            }
        except Exception as e:
            print(f"Error calculating usage stats: {e}")
            return None

    # --- PARTS ---
    def search_parts(self, query_str, limit=15):
        try:
            with self._get_connection() as conn:
                keywords = query_str.split()
                conditions = []
                params = []
                for k in keywords:
                    conditions.append("(Description LIKE ? OR Part_Number LIKE ? OR Category LIKE ?)")
                    wildcard_k = f"%{k}%"
                    params.extend([wildcard_k, wildcard_k, wildcard_k])
                
                where_clause = " AND ".join(conditions)
                query = f"SELECT Category, Part_Number, Description, Price_Euro, Image_URL FROM parts WHERE {where_clause} LIMIT {limit}"
                return pd.read_sql(query, conn, params=params)
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error searching parts: {e}")
            return pd.DataFrame()

    def get_part_images_for_ai(self, conditions):
        try:
            with self._get_connection() as conn:
                where_clause_img = " OR ".join(conditions)
                query_img = f"SELECT Category, Image_URL FROM parts WHERE ({where_clause_img}) AND Image_URL != 'No Image' LIMIT 1"
                return pd.read_sql(query_img, conn)
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"Error retrieving part images: {e}")
            return pd.DataFrame()

    def seed_custom_rules(self):
        """Seeds the custom_mechanic_rules table with initial data."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM custom_mechanic_rules")
                if cursor.fetchone()[0] == 0:
                    rules = [
                        ('Optimal variator weights are 18g or 19g',),
                        ('The clutch nut socket size is definitively NOT 27mm',)
                    ]
                    cursor.executemany("INSERT INTO custom_mechanic_rules (rule_text) VALUES (?)", rules)
                    conn.commit()
        except sqlite3.Error as e:
            print(f"Error seeding custom rules: {e}")
