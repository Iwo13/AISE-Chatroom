from flask import Flask, request, redirect, render_template, make_response
from datetime import datetime
import os
import json

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

# ── Storage: PostgreSQL wenn DATABASE_URL gesetzt, sonst JSON-Datei ──
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_conn():
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

    def init_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        sender TEXT NOT NULL,
                        text TEXT NOT NULL,
                        time TEXT NOT NULL
                    )
                ''')

    def load_messages():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT sender, text, time FROM messages ORDER BY id')
                return [dict(r) for r in cur.fetchall()]

    def add_message(sender, text, time):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO messages (sender, text, time) VALUES (%s, %s, %s)',
                    (sender, text, time)
                )

    init_db()

else:
    MESSAGES_FILE = 'messages.json'

    def load_messages():
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def add_message(sender, text, time):
        messages = load_messages()
        messages.append({'sender': sender, 'text': text, 'time': time})
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)


# ── Flask-Route ───────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    name = request.cookies.get('username', '').strip()
    messages = load_messages()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'set_name':
            new_name = request.form.get('name', '').strip()
            if not new_name:
                return render_template('index.html', name='', messages=messages,
                                       name_error='Bitte gib einen Namen ein.')
            resp = make_response(redirect('/'))
            resp.set_cookie('username', new_name, max_age=86400)
            return resp

        if action == 'send_message':
            if not name:
                return redirect('/')
            text = request.form.get('message', '').strip()
            if text and len(text) <= 500:
                add_message(name, text, datetime.now().strftime('%H:%M · %d.%m.%Y'))
            return redirect('/#bottom')

    return render_template('index.html', name=name, messages=messages)
