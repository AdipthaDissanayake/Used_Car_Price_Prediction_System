"""
Database Management Module for Used Car Price Prediction System
Supports MySQL via PyMySQL and built-in SQLite fallback (zero C-extension dependencies)
Handles User Registration, Hashed Password Authentication, and User-Specific Prediction History.
"""

import os
import sqlite3
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://finassist_app:root@localhost:3306/used_car_price_db'
)


class DatabaseManager:
    """Handles connection, migrations, user persistence, auth, and prediction logging."""

    def __init__(self, db_url=None):
        self.db_url = db_url or DATABASE_URL
        self.is_mysql = False
        self.config = {}
        self._parse_url()

    def _parse_url(self):
        url = self.db_url
        if url.startswith('mysql') or 'pymysql' in url:
            self.is_mysql = True
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
        """Create tables if they do not exist and apply migrations."""
        conn = self.get_connection()
        try:
            if self.is_mysql:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            email VARCHAR(255) NOT NULL UNIQUE,
                            password_hash VARCHAR(255) NOT NULL,
                            name VARCHAR(255),
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            last_login DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        );
                    """)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS prediction_logs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            user_id INT NOT NULL,
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
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        );
                    """)
                print(f"[DB] Initialized MySQL database '{self.config.get('database')}'.")
            else:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS prediction_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
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
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                """)
                conn.commit()
                print(f"[DB] Initialized SQLite database '{self.sqlite_path}'.")
        finally:
            conn.close()

    def register_user(self, email, password, name=None):
        """Register a user with hashed password."""
        email = email.strip().lower()
        conn = self.get_connection()
        try:
            pw_hash = generate_password_hash(password)
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if self.is_mysql:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                    if cur.fetchone():
                        return None, "An account with this email address already exists."

                    sql = """
                        INSERT INTO users (email, password_hash, name, created_at, last_login)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cur.execute(sql, (email, pw_hash, name or email.split('@')[0], now, now))
                    user_id = cur.lastrowid
                    return {
                        'id': user_id,
                        'email': email,
                        'name': name or email.split('@')[0],
                        'created_at': now
                    }, None
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cur.fetchone():
                    return None, "An account with this email address already exists."

                cur.execute("""
                    INSERT INTO users (email, password_hash, name, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, pw_hash, name or email.split('@')[0], now, now))
                conn.commit()
                user_id = cur.lastrowid
                return {
                    'id': user_id,
                    'email': email,
                    'name': name or email.split('@')[0],
                    'created_at': now
                }, None
        except Exception as e:
            print(f"[DB Error] Registration failure: {e}")
            return None, str(e)
        finally:
            conn.close()

    def authenticate_user(self, email, password):
        """Authenticate user with email and password."""
        email = email.strip().lower()
        conn = self.get_connection()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if self.is_mysql:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, email, password_hash, name, created_at, last_login FROM users WHERE email = %s", (email,))
                    row = cur.fetchone()
                    if not row or not row.get('password_hash'):
                        return None, "Invalid email or password."

                    if not check_password_hash(row['password_hash'], password):
                        return None, "Invalid email or password."

                    cur.execute("UPDATE users SET last_login = %s WHERE id = %s", (now, row['id']))
                    del row['password_hash']
                    if isinstance(row.get('created_at'), datetime):
                        row['created_at'] = row['created_at'].isoformat()
                    if isinstance(row.get('last_login'), datetime):
                        row['last_login'] = row['last_login'].isoformat()
                    return row, None
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cur.fetchone()
                if not row or not row['password_hash']:
                    return None, "Invalid email or password."

                if not check_password_hash(row['password_hash'], password):
                    return None, "Invalid email or password."

                cur.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, row['id']))
                conn.commit()
                res = dict(row)
                del res['password_hash']
                return res, None
        except Exception as e:
            print(f"[DB Error] Authentication failure: {e}")
            return None, str(e)
        finally:
            conn.close()

    def log_prediction(self, payload, predicted_price, log_price, user_id):
        """Save user-specific car prediction record."""
        if not user_id:
            return None

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
                        'transmission': payload.get('transmission'),
                        'clean_title': payload.get('clean_title'),
                        'accident': payload.get('accident'),
                        'fuel_type': payload.get('fuel_type'),
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
                    'transmission': payload.get('transmission'),
                    'clean_title': payload.get('clean_title'),
                    'accident': payload.get('accident'),
                    'fuel_type': payload.get('fuel_type'),
                    'predicted_price': round(float(predicted_price), 2),
                    'predicted_price_formatted': f"${float(predicted_price):,.2f}",
                    'created_at': now
                }
        except Exception as e:
            print(f"[DB Error] Failed to log prediction: {e}")
            return None
        finally:
            conn.close()

    def get_user_predictions(self, user_id, limit=20):
        """Retrieve prediction history strictly for a specific user."""
        if not user_id:
            return []

        conn = self.get_connection()
        try:
            if self.is_mysql:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM prediction_logs WHERE user_id = %s ORDER BY id DESC LIMIT %s",
                        (user_id, limit)
                    )
                    rows = cur.fetchall()
                    for r in rows:
                        if isinstance(r.get('created_at'), datetime):
                            r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                        r['predicted_price_formatted'] = f"${r['predicted_price']:,.2f}"
                    return rows
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM prediction_logs WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                    (user_id, limit)
                )
                rows = [dict(r) for r in cur.fetchall()]
                for r in rows:
                    r['predicted_price_formatted'] = f"${r['predicted_price']:,.2f}"
                return rows
        except Exception as e:
            print(f"[DB Error] Failed to fetch prediction history: {e}")
            return []
        finally:
            conn.close()

    def delete_prediction_log(self, log_id, user_id):
        """Delete an individual prediction log strictly owned by user_id."""
        conn = self.get_connection()
        try:
            if self.is_mysql:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM prediction_logs WHERE id = %s AND user_id = %s",
                        (log_id, user_id)
                    )
                    return cur.rowcount > 0
            else:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM prediction_logs WHERE id = ? AND user_id = ?",
                    (log_id, user_id)
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"[DB Error] Failed to delete prediction: {e}")
            return False
        finally:
            conn.close()

    def clear_user_predictions(self, user_id):
        """Delete all prediction history for a specific user."""
        conn = self.get_connection()
        try:
            if self.is_mysql:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM prediction_logs WHERE user_id = %s", (user_id,))
                    return cur.rowcount
            else:
                cur = conn.cursor()
                cur.execute("DELETE FROM prediction_logs WHERE user_id = ?", (user_id,))
                conn.commit()
                return cur.rowcount
        except Exception as e:
            print(f"[DB Error] Failed to clear history: {e}")
            return 0
        finally:
            conn.close()


# Global database instance
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    return db_manager
