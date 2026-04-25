import sqlite3
import pandas as pd
import json
import os
import logging
from datetime import date, datetime
import config

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 2

_MIGRATIONS = {
    1: [
        "CREATE INDEX IF NOT EXISTS idx_mh_date ON maintenance_history(date)",
        "CREATE INDEX IF NOT EXISTS idx_mh_km ON maintenance_history(km)",
        "CREATE INDEX IF NOT EXISTS idx_mh_task ON maintenance_history(task)",
        "CREATE INDEX IF NOT EXISTS idx_fuel_date ON fuel_logs(date)",
        "CREATE INDEX IF NOT EXISTS idx_parts_desc ON parts(Description)",
        "CREATE INDEX IF NOT EXISTS idx_parts_pn ON parts(Part_Number)",
    ],
    2: [
        """CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )""",
    ],
}


class ScooterDB:
    def __init__(self, db_path, data_file):
        self.db_path = db_path
        self.data_file = data_file
        self.init_db()
        self.seed_tech_specs()
        self.seed_custom_rules()
        self.migrate_if_needed()
        self._run_migrations()

    def _get_connection(self):
        try:
            return sqlite3.connect(self.db_path, timeout=10.0)
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def init_db(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

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

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS vehicle_stats (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')

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

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tech_specs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        spec_name TEXT NOT NULL,
                        spec_value TEXT NOT NULL,
                        unit TEXT
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fuel_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        km INTEGER NOT NULL,
                        liters REAL NOT NULL,
                        price REAL
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS todo_list (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT NOT NULL,
                        priority TEXT DEFAULT 'Medium',
                        status TEXT DEFAULT 'Pending',
                        added_date TEXT NOT NULL
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS custom_mechanic_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rule_text TEXT NOT NULL
                    )
                ''')

                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def _run_migrations(self):
        with self._get_connection() as conn:
            current = conn.execute("PRAGMA user_version").fetchone()[0]
            for version in range(current + 1, CURRENT_SCHEMA_VERSION + 1):
                for sql in _MIGRATIONS[version]:
                    conn.execute(sql)
                conn.execute(f"PRAGMA user_version = {version}")
            conn.commit()

    # --- CUSTOM RULES ---
    def get_custom_mechanic_rules(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT rule_text FROM custom_mechanic_rules")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving custom rules: {e}")
            return []

    def add_custom_mechanic_rule(self, rule_text):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO custom_mechanic_rules (rule_text) VALUES (?)", (rule_text,))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding custom rule: {e}")
            raise

    # --- TODO / REPAIRS ---
    def add_todo_item(self, task, priority):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO todo_list (task, priority, added_date) VALUES (?, ?, ?)",
                    (task, priority, str(date.today()))
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding todo item: {e}")
            raise

    def get_todo_list(self):
        try:
            with self._get_connection() as conn:
                query = "SELECT id, task, priority, status, added_date FROM todo_list WHERE status = 'Pending' ORDER BY priority DESC"
                return pd.read_sql(query, conn)
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            logger.error(f"Error retrieving todo list: {e}")
            return pd.DataFrame()

    def complete_todo_item(self, item_id):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE todo_list SET status = 'Completed' WHERE id = ?", (int(item_id),))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error completing todo item: {e}")
            raise

    # --- FUEL LOGS ---
    def add_fuel_log(self, date_str, km, liters, price):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO fuel_logs (date, km, liters, price) VALUES (?, ?, ?, ?)",
                    (date_str, km, liters, price)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding fuel log: {e}")
            raise

    def get_fuel_history(self):
        try:
            with self._get_connection() as conn:
                query = "SELECT date, km, liters, price FROM fuel_logs ORDER BY date ASC"
                df = pd.read_sql(query, conn)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df['km_diff'] = df['km'].diff().replace(0, pd.NA)
                    df['l_100km'] = (df['liters'] / df['km_diff']) * 100
                return df
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            logger.error(f"Error retrieving fuel history: {e}")
            return pd.DataFrame()

    def seed_tech_specs(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tech_specs")
                if cursor.fetchone()[0] > 0:
                    return
                cursor.executemany(
                    "INSERT INTO tech_specs (category, spec_name, spec_value, unit) VALUES (?, ?, ?, ?)",
                    config.TECH_SPECS_SEED
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error seeding tech specs: {e}")

    def get_tech_specs(self):
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
                    "unit": row['unit'],
                })
            return {"status": "success", "data": structured_data}

        except sqlite3.Error as e:
            return {"status": "error", "message": f"Database error: {str(e)}"}

    def migrate_if_needed(self):
        if not os.path.exists(self.data_file):
            return
        logger.info(f"Migrating data from {self.data_file}...")
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Only update mileage from JSON if it's higher than current DB value
            json_mileage = data.get('mileage', 0)
            if json_mileage > self.get_mileage():
                with self._get_connection() as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO vehicle_stats (key, value) VALUES ('mileage', ?)",
                        (str(json_mileage),)
                    )
                    conn.commit()

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM maintenance_history")
                if cursor.fetchone()[0] == 0:
                    for entry in data.get('history', []):
                        cursor.execute(
                            "INSERT INTO maintenance_history (date, task, km, cost, notes) VALUES (?, ?, ?, ?, ?)",
                            (entry['date'], entry['task'], entry['km'], entry['cost'], entry['notes'])
                        )
                conn.commit()

            os.rename(self.data_file, self.data_file + ".bak")
            logger.info("Migration completed successfully.")
        except Exception as e:
            logger.error(f"Error during migration: {e}")

    # --- MILEAGE ---
    def get_mileage(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM vehicle_stats WHERE key = 'mileage'")
                row = cursor.fetchone()
                return int(row[0]) if row else 0
        except sqlite3.Error as e:
            logger.error(f"Error retrieving mileage: {e}")
            return 0

    def update_mileage(self, new_km):
        current = self.get_mileage()
        if new_km < current:
            raise ValueError(f"New mileage ({new_km:,}) cannot be less than current ({current:,} km)")
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO vehicle_stats (key, value) VALUES ('mileage', ?)",
                    (str(new_km),)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating mileage: {e}")
            raise

    # --- HISTORY ---
    def get_history(self):
        try:
            with self._get_connection() as conn:
                query = "SELECT date, task, km, cost, notes FROM maintenance_history ORDER BY date DESC, km DESC"
                df = pd.read_sql(query, conn)
                return df.to_dict('records')
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            logger.error(f"Error retrieving history: {e}")
            return []

    def get_last_service_km(self, keywords):
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
            logger.error(f"Error retrieving last service KM: {e}")
            return 0

    def add_service_log(self, date_str, task, km, cost, notes):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO maintenance_history (date, task, km, cost, notes) VALUES (?, ?, ?, ?, ?)",
                    (date_str, task, km, cost, notes)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding service log: {e}")
            raise

    # --- UTILITIES ---
    def calculate_usage_stats(self):
        try:
            history = self.get_history()
            if not history or len(history) < 2:
                return None

            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            first_date = df['date'].min()
            days_diff = (pd.Timestamp.now() - first_date).days

            if days_diff <= 0:
                return None

            total_km_tracked = self.get_mileage() - df['km'].min()
            avg_km_day = total_km_tracked / days_diff

            return {
                "avg_km_day": avg_km_day,
                "avg_km_month": avg_km_day * 30.44,
                "days_tracked": days_diff,
            }
        except Exception as e:
            logger.error(f"Error calculating usage stats: {e}")
            return None

    # --- PARTS ---
    def search_parts(self, query_str, limit=15):
        try:
            with self._get_connection() as conn:
                keywords = query_str.split()
                if not keywords:
                    return pd.DataFrame()
                conditions = []
                params = []
                for k in keywords:
                    conditions.append("(Description LIKE ? OR Part_Number LIKE ? OR Category LIKE ?)")
                    wildcard_k = f"%{k}%"
                    params.extend([wildcard_k, wildcard_k, wildcard_k])

                where_clause = " AND ".join(conditions)
                query = f"SELECT Category, Part_Number, Description, Price_Euro, Image_URL FROM parts WHERE {where_clause} LIMIT ?"
                params.append(limit)
                return pd.read_sql(query, conn, params=params)
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            logger.error(f"Error searching parts: {e}")
            return pd.DataFrame()

    def get_part_images_for_ai(self, keywords):
        if not keywords:
            return pd.DataFrame()
        try:
            with self._get_connection() as conn:
                conditions = " OR ".join(
                    ["(Description LIKE ? OR Category LIKE ?)" for _ in keywords]
                )
                params = []
                for k in keywords:
                    params.extend([f"%{k}%", f"%{k}%"])
                query = f"SELECT Category, Image_URL FROM parts WHERE ({conditions}) AND Image_URL != 'No Image' LIMIT 1"
                return pd.read_sql(query, conn, params=params)
        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            logger.error(f"Error retrieving part images: {e}")
            return pd.DataFrame()

    def seed_custom_rules(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM custom_mechanic_rules")
                if cursor.fetchone()[0] == 0:
                    rules = [
                        ('Optimal variator weights are 18g or 19g',),
                        ('The clutch nut socket size is definitively NOT 27mm',),
                    ]
                    cursor.executemany("INSERT INTO custom_mechanic_rules (rule_text) VALUES (?)", rules)
                    conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error seeding custom rules: {e}")

    def seed_parts(self, parts_data):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM parts")
                if cursor.fetchone()[0] > 0:
                    logger.info("Parts table already seeded, skipping.")
                    return
                cursor.executemany(
                    "INSERT INTO parts (Part_Number, Description, Category, Price_Euro, Image_URL) VALUES (?, ?, ?, ?, ?)",
                    parts_data
                )
                conn.commit()
                logger.info(f"Seeded {len(parts_data)} parts.")
        except sqlite3.Error as e:
            logger.error(f"Error seeding parts: {e}")
            raise

    # --- CHAT HISTORY ---
    def save_chat_message(self, role, content):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO chat_history (timestamp, role, content) VALUES (?, ?, ?)",
                    (datetime.now().isoformat(), role, content)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving chat message: {e}")

    def get_chat_history(self, limit=50):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving chat history: {e}")
            return []

    def clear_chat_history(self):
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM chat_history")
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error clearing chat history: {e}")
