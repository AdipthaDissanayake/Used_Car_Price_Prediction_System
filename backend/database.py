"""
Database Management Module for Used Car Price Prediction System
Supports MySQL via PyMySQL and built-in SQLite fallback (zero C-extension dependencies)
"""

import os
import sqlite3
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
import pymysql
import pymysql.cursors

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://finassist_app:root@localhost:3306/used_car_price_db'
)


class DatabaseManager:
    """Handles connection, migrations, user persistence, and prediction logging."""

    def __init__(self, db_url=None):
        self.db_url = db_url or DATABASE_URL
        self.is_mysql = False
        self.config = {}
        self._parse_url()

    def _parse_url(self):
        url = self.db_url
        if url.startswith('mysql') or 'pymysql' in url:
            self.is_mysql = True
            # Clean protocol prefix for urllib parsing
            clean_url = url.replace('mysql+pymysql://', 'mysql://')
            parsed = urllib.parse.urlparse(clean_url)
            self.config = {
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or 3306,
                'user': urllib.parse.unquote(parsed.username or 'root'),
                'password': urllib.parse.unquote(parsed.password or ''),
                'database': parsed.path.lstrip('/') or 'used_car_price_db',
                'cursorclass': pymysql.cursors.DictCursor,
                'autocommit': True,
                'connect_timeout': 5
            }
        else:
            self.is_mysql = False
            self.sqlite_path = 'used_car_price_fallback.db'

    def get_connection(self):
        """Obtain a live database connection with automatic fallback."""
        if self.is_mysql:
            try:
                return pymysql.connect(**self.config)
            except Exception as e:
                print(f"[DB Warning] MySQL connection failed ({e}). Falling back to SQLite.")
                self.is_mysql = False
                self.sqlite_path = 'used_car_price_fallback.db'
                return sqlite3.connect(self.sqlite_path)
        else:
            return sqlite3.connect(self.sqlite_path)

    def init_db(self):
        """Create tables if they do not exist."""
        conn = self.get_connection()
        try:
            if self.is_mysql:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            google_id VARCHAR(255) NOT NULL UNIQUE,
                            email VARCHAR(255) NOT NULL UNIQUE,
                            name VARCHAR(255),
                            picture VARCHAR(1024),
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            last_login DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        );
                    """)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS prediction_logs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            user_id INT,
                            brand VARCHAR(100) NOT NULL,
                            model_year INT NOT NULL,
                            milage DOUBLE NOT NULL,
                            transmission VARCHAR(100) NOT NULL,
                            clean_title VARCHAR(10) NOT NULL,
                            accident VARCHAR(150) NOT NULL,
                            fuel_type VARCHAR(100) NOT NULL,
                            predicted_price DOUBLE NOT NULL,
                            log_price DOUBLE NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                        );
                    """)
                print(f"[DB] Initialized MySQL database '{self.config.get('database')}'.")
            else:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        google_id TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        name TEXT,
                        picture TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS prediction_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        brand TEXT NOT NULL,
                        model_year INTEGER NOT NULL,
                        milage REAL NOT NULL,
                        transmission TEXT NOT NULL,
                        clean_title TEXT NOT NULL,
                        accident TEXT NOT NULL,
                        fuel_type TEXT NOT NULL,
                        predicted_price REAL NOT NULL,
                        log_price REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                    );
                """)
                conn.commit()
                print(f"[DB] Initialized SQLite database '{self.sqlite_path}'.")
        finally:
            conn.close()

    def save_or_update_user(self, google_id, email, name=None, picture=None):
        """Insert or update user record from Google Auth."""
        conn = self.get_connection()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if self.is_mysql:
                with conn.cursor() as cur:
                    sql = """
                        INSERT INTO users (google_id, email, name, picture, created_at, last_login)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            picture = VALUES(picture),
                            last_login = VALUES(last_login);
                    """
                    cur.execute(sql, (google_id, email, name, picture, now, now))
                    cur.execute("SELECT id, google_id, email, name, picture, created_at, last_login FROM users WHERE google_id = %s", (google_id,))
                    row = cur.fetchone()
                    if row and isinstance(row.get('created_at'), datetime):
                        row['created_at'] = row['created_at'].isoformat()
                    if row and isinstance(row.get('last_login'), datetime):
                        row['last_login'] = row['last_login'].isoformat()
                    return row
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
                user = cur.fetchone()
                if not user:
                    cur.execute("""
                        INSERT INTO users (google_id, email, name, picture, created_at, last_login)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (google_id, email, name, picture, now, now))
                else:
                    cur.execute("""
                        UPDATE users SET name = ?, picture = ?, last_login = ? WHERE google_id = ?
                    """, (name, picture, now, google_id))
                conn.commit()
                cur.execute("SELECT id, google_id, email, name, picture, created_at, last_login FROM users WHERE google_id = ?", (google_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"[DB Error] Failed to save/update user: {e}")
            return None
        finally:
            conn.close()

    def log_prediction(self, payload, predicted_price, log_price, user_id=None):
        """Save car prediction record."""
        conn = self.get_connection()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if self.is_mysql:
                with conn.cursor() as cur:
                    sql = """
                        INSERT INTO prediction_logs 
                        (user_id, brand, model_year, milage, transmission, clean_title, accident, fuel_type, predicted_price, log_price, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(sql, (
                        user_id,
                        str(payload.get('brand')),
                        int(payload.get('model_year')),
                        float(payload.get('milage')),
                        str(payload.get('transmission')),
                        str(payload.get('clean_title')),
                        str(payload.get('accident')),
                        str(payload.get('fuel_type')),
                        float(predicted_price),
                        float(log_price),
                        now
                    ))
                    last_id = cur.lastrowid
                    return {
                        'id': last_id,
                        'user_id': user_id,
                        'brand': payload.get('brand'),
                        'model_year': payload.get('model_year'),
                        'milage': payload.get('milage'),
                        'predicted_price': round(float(predicted_price), 2),
                        'predicted_price_formatted': f"${float(predicted_price):,.2f}",
                        'created_at': now
                    }
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO prediction_logs 
                    (user_id, brand, model_year, milage, transmission, clean_title, accident, fuel_type, predicted_price, log_price, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    str(payload.get('brand')),
                    int(payload.get('model_year')),
                    float(payload.get('milage')),
                    str(payload.get('transmission')),
                    str(payload.get('clean_title')),
                    str(payload.get('accident')),
                    str(payload.get('fuel_type')),
                    float(predicted_price),
                    float(log_price),
                    now
                ))
                conn.commit()
                last_id = cur.lastrowid
                return {
                    'id': last_id,
                    'user_id': user_id,
                    'brand': payload.get('brand'),
                    'model_year': payload.get('model_year'),
                    'milage': payload.get('milage'),
                    'predicted_price': round(float(predicted_price), 2),
                    'predicted_price_formatted': f"${float(predicted_price):,.2f}",
                    'created_at': now
                }
        except Exception as e:
            print(f"[DB Error] Failed to log prediction: {e}")
            return None
        finally:
            conn.close()

    def get_recent_predictions(self, user_id=None, limit=10):
        """Retrieve recent predictions, optionally filtered by user_id."""
        conn = self.get_connection()
        try:
            if self.is_mysql:
                with conn.cursor() as cur:
                    if user_id:
                        cur.execute("SELECT * FROM prediction_logs WHERE user_id = %s ORDER BY id DESC LIMIT %s", (user_id, limit))
                    else:
                        cur.execute("SELECT * FROM prediction_logs ORDER BY id DESC LIMIT %s", (limit,))
                    rows = cur.fetchall()
                    for r in rows:
                        if isinstance(r.get('created_at'), datetime):
                            r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                        r['predicted_price_formatted'] = f"${r['predicted_price']:,.2f}"
                    return rows
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                if user_id:
                    cur.execute("SELECT * FROM prediction_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
                else:
                    cur.execute("SELECT * FROM prediction_logs ORDER BY id DESC LIMIT ?", (limit,))
                rows = [dict(r) for r in cur.fetchall()]
                for r in rows:
                    r['predicted_price_formatted'] = f"${r['predicted_price']:,.2f}"
                return rows
        except Exception as e:
            print(f"[DB Error] Failed to fetch prediction history: {e}")
            return []
        finally:
            conn.close()


# Global database instance
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    return db_manager
