from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv('DB_HOST', 'database')
DB_USER = os.getenv('MYSQL_USER', 'bloguser')
DB_PASS = os.getenv('MYSQL_PASSWORD', 'blogpass')
DB_NAME = os.getenv('MYSQL_DATABASE', 'blogdb')
DB_PORT = int(os.getenv('DB_PORT', 3306))

def get_conn():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME, port=DB_PORT,
                           cursorclass=pymysql.cursors.DictCursor, autocommit=True)

@app.route('/posts', methods=['GET'])
def list_posts():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, content, created_at FROM posts ORDER BY created_at DESC;")
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json() or {}
    title = data.get('title')
    content = data.get('content','')
    if not title:
        return jsonify({'error': 'title is required'}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO posts (title, content) VALUES (%s, %s);", (title, content))
        post_id = cur.lastrowid
        cur.execute("SELECT id, title, content, created_at FROM posts WHERE id=%s;", (post_id,))
        post = cur.fetchone()
    conn.close()
    return jsonify(post), 201

@app.route('/')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
