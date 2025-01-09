from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Database setup
def init_db():
    with sqlite3.connect('chat.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT)')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        with sqlite3.connect('chat.db') as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('chat.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['username'] = username  # Store username in session
                return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' in session:
        message = request.form['message']
        user_id = session['user_id']
        with sqlite3.connect('chat.db') as conn:
            conn.execute('INSERT INTO messages (user_id, message) VALUES (?, ?)', (user_id, message))
    return redirect(url_for('chat'))

@app.route('/get_messages')
def get_messages():
    with sqlite3.connect('chat.db') as conn:
        messages = conn.execute('SELECT messages.message, users.username FROM messages JOIN users ON messages.user_id = users.id ORDER BY messages.id DESC').fetchall()
    return jsonify(messages)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
