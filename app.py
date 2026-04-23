from flask import Flask, request, redirect, render_template, make_response
from datetime import datetime

app = Flask(__name__)
messages = []

@app.route('/', methods=['GET', 'POST'])
def index():
    name = request.cookies.get('username', '').strip()

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
            return redirect('/#bottom')

    return render_template('index.html', name=name, messages=messages)
