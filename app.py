from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import webbrowser
from threading import Timer
from datetime import datetime

app = Flask(__name__)
# DATABASE
def init_db():

    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        category TEXT,
        priority TEXT,
        sentiment TEXT,
        created_at TEXT
    )
''')

    conn.commit()
    conn.close()

init_db()


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/index.html")

# HOME
@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

# ABOUT
@app.route('/about.html')
def about():
    return render_template('about.html')

# FEATURES
@app.route('/features.html')
def features():
    return render_template('features.html')

# ANALYSIS
@app.route('/analysis.html')
def analysis():
    return render_template('analysis.html')

# HOW IT WORKS
@app.route('/howitworks.html')
def howitworks():
    return render_template('howitworks.html')


# SAVE TICKET
@app.route('/save_ticket', methods=['POST'])
def save_ticket():

    data = request.json

    message = data.get('message')
    category = data.get('category')
    priority = data.get('priority')
    sentiment = data.get('sentiment')

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO tickets
        (message, category, priority, sentiment, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            message,
            category,
            priority,
            sentiment,
            created_at
        )
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})

# CSV UPLOAD
@app.route('/upload_csv', methods=['POST'])
def upload_csv():

    file = request.files['file']

    df = pd.read_csv(file)

    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()

    for index, row in df.iterrows():

        message = str(row.get('message', ''))
        category = str(row.get('category', 'General'))
        priority = str(row.get('priority', 'Medium'))
        sentiment = str(row.get('sentiment', 'Neutral'))

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            INSERT INTO tickets
            (message, category, priority, sentiment, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            message,
            category,
            priority,
            sentiment,
            created_at
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "rows_added": len(df)
    })

# GET HISTORY
@app.route('/get_history')
def get_history():

    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()

    c.execute("""
        SELECT message, category,
        priority, sentiment, created_at
        FROM tickets
        ORDER BY id DESC
    """)

    rows = c.fetchall()

    conn.close()

    history = []

    for row in rows:

        history.append({
            "message": row[0],
            "category": row[1],
            "priority": row[2],
            "sentiment": row[3],
            "created_at": row[4]
        })

    return jsonify(history)

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)