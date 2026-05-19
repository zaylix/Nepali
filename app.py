from flask import Flask, jsonify, request
import sqlite3
import os
import json
from threading import Thread

app = Flask(__name__)

# Configuration
DB_NAME = "database.db"
API_KEY = "diwazz"
JSON_PARTS_DIR = "data_parts"

def validate_nepali_number(number: str):
    if not number.isdigit() or len(number) != 10:
        return False
    prefix = number[:3]
    valid_prefixes = ["984", "985", "986", "974", "975", "976", "972", "980", "981", "982", "961", "962", "988"]
    return prefix in valid_prefixes

def init_sqlite_db():
    """Initialize SQLite database from JSON parts if it doesn't exist."""
    if os.path.exists(DB_NAME):
        print("SQLite database already exists.")
        return

    print("Initializing SQLite database from JSON parts...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (mobile TEXT PRIMARY KEY, data TEXT)')
    
    if os.path.exists(JSON_PARTS_DIR):
        parts = sorted([f for f in os.listdir(JSON_PARTS_DIR) if f.endswith('.json')])
        for part in parts:
            print(f"Processing {part}...")
            with open(os.path.join(JSON_PARTS_DIR, part), 'r') as f:
                data = json.load(f)
                batch = [(item['mobile'], json.dumps(item)) for item in data]
                c.executemany('INSERT OR IGNORE INTO users VALUES (?, ?)', batch)
                conn.commit()
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_mobile ON users(mobile)')
    conn.commit()
    conn.close()
    print("SQLite database initialization complete.")

# Initialize DB in background
Thread(target=init_sqlite_db).start()

@app.route('/')
def home():
    return jsonify({
        "message": "Nepali 1GB+ Advanced Info API is running",
        "dev": "@diwazz",
        "status": "Ready" if os.path.exists(DB_NAME) else "Initializing Database..."
    })

@app.route('/api/key=<key>/num=<number>')
def get_info(key, number):
    if key != API_KEY:
        return jsonify({"success": False, "message": "Invalid API Key"}), 403
    
    if not validate_nepali_number(number):
        return jsonify({
            "success": False, 
            "message": "Invalid Only Number for Nepali",
            "number": number
        }), 400
    
    if not os.path.exists(DB_NAME):
        return jsonify({"success": False, "message": "Database is still initializing, please wait..."}), 503

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT data FROM users WHERE mobile = ?', (number,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                "success": True,
                "data": [json.loads(row[0])],
                "count": 1
            })
        else:
            return jsonify({
                "success": False,
                "message": "Number not found in database",
                "number": number
            }), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
