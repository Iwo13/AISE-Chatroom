from flask import Flask, request, redirect, render_template, make_response
from datetime import datetime
import json
import os

app = Flask(__name__)

MESSAGES_FILE = 'messages.json'

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

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
                messages.append({
                    'sender': name,
                    'text': text,
                    'time': datetime.now().strftime('%H:%M · %d.%m.%Y'),
                })
                save_messages(messages)
            return redirect('/#bottom')

    return render_template('index.html', name=name, messages=messages)
