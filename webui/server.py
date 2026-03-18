"""
Z-Ray Medical Platform — Flask API Server
==========================================
Lightweight backend with SQLite, bcrypt auth, and JWT sessions.
Run:  python server.py
"""

import os
import datetime
import sqlite3
from functools import wraps

from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import jwt

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'zray.db')
SECRET_KEY = os.environ.get('ZRAY_SECRET', 'zray-dev-secret-change-in-prod')
JWT_EXP_HOURS = 8

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)
bcrypt = Bcrypt(app)

# ──────────────────────────────────────────────
# Database helpers
# ──────────────────────────────────────────────
def get_db():
    """Get a per-request database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA journal_mode=WAL')
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and seed default admin user."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            full_name   TEXT,
            address     TEXT,
            license_no  TEXT,
            role        TEXT DEFAULT 'doctor',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        cur.execute('ALTER TABLE users ADD COLUMN address TEXT')
        cur.execute('ALTER TABLE users ADD COLUMN license_no TEXT')
    except sqlite3.OperationalError:
        pass # Columns already exist

    cur.execute('''
        CREATE TABLE IF NOT EXISTS patient_records (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id      TEXT NOT NULL,
            patient_age     INTEGER,
            patient_gender  TEXT,
            analysis_type   TEXT NOT NULL,
            diagnosis       TEXT,
            confidence      REAL,
            severity        TEXT,
            description     TEXT,
            created_by      INTEGER REFERENCES users(id),
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed default admin if not exists
    existing = cur.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not existing:
        hashed = bcrypt.generate_password_hash('admin').decode('utf-8')
        cur.execute(
            'INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)',
            ('admin', hashed, 'Administrator', 'admin')
        )
        print('✔  Default admin user created (admin / admin)')

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# JWT helpers
# ──────────────────────────────────────────────
def create_token(user_id, username, role):
    payload = {
        'sub': str(user_id),
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXP_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def token_required(f):
    """Decorator that requires a valid JWT in the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth[7:]

        if not token:
            print("Token validation failed: Token missing in Authorization header")
            return jsonify({'error': 'Token missing'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.current_user = data
        except jwt.ExpiredSignatureError:
            print("Token validation failed: Token expired")
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError as e:
            print(f"Token validation failed: Invalid token - {e}")
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401

        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────
# API Routes
# ──────────────────────────────────────────────

# --- Auth ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    address = data.get('address', '').strip()
    license_no = data.get('license_no', '').strip()

    if not username or not password or not full_name:
        return jsonify({'error': 'Username, password, and full name are required'}), 400

    db = get_db()
    existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        return jsonify({'error': 'Username/Email already exists'}), 409

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        cur = db.execute('''
            INSERT INTO users (username, password, full_name, address, license_no, role)
            VALUES (?, ?, ?, ?, ?, 'doctor')
        ''', (username, hashed, full_name, address, license_no))
        db.commit()
        return jsonify({'message': 'Registration successful', 'id': cur.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': f'Failed to register: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    token = create_token(user['id'], user['username'], user['role'])
    return jsonify({
        'token': token,
        'username': user['username'],
        'full_name': user['full_name'],
        'role': user['role']
    })


# --- Patient Records ---
@app.route('/api/records', methods=['GET'])
@token_required
def get_records():
    db = get_db()
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    rows = db.execute(
        'SELECT * FROM patient_records ORDER BY created_at DESC LIMIT ? OFFSET ?',
        (limit, offset)
    ).fetchall()

    total = db.execute('SELECT COUNT(*) FROM patient_records').fetchone()[0]

    return jsonify({
        'total': total,
        'records': [dict(r) for r in rows]
    })


@app.route('/api/records', methods=['POST'])
@token_required
def create_record():
    data = request.get_json(silent=True) or {}

    required = ['patient_id', 'analysis_type']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    db = get_db()
    cur = db.execute('''
        INSERT INTO patient_records
            (patient_id, patient_age, patient_gender, analysis_type,
             diagnosis, confidence, severity, description, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['patient_id'],
        data.get('patient_age'),
        data.get('patient_gender'),
        data['analysis_type'],
        data.get('diagnosis'),
        data.get('confidence'),
        data.get('severity'),
        data.get('description'),
        g.current_user['sub']
    ))
    db.commit()

    return jsonify({'id': cur.lastrowid, 'message': 'Record saved'}), 201


# --- Serve frontend ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print(f'🚀 Z-Ray API server running at http://localhost:5000')
    print(f'📂 Database: {DB_PATH}')
    app.run(host='0.0.0.0', port=5000, debug=True)
