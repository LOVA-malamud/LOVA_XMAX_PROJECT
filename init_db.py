import sqlite3
import os

# הגדרת הנתיב המדויק לתיקייה שהשארת
db_path = os.path.join("xmax_docs.docs", "xmax_parts_database.db")

def create_database():
    # יצירת ה-DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # יצירת טבלה בסיסית (תוסיף עמודות לפי הצורך)
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
    
    conn.commit()
    conn.close()
    print(f"Database created successfully at: {db_path}")

if __name__ == "__main__":
    create_database()