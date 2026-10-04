import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os

app = Flask(__name__)
app.secret_key = 'namu_cloud_secret_key'

# 디스코드 웹훅 URL (고객센터 알림용)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1556181193605652572/ETCZvr3siPMwcn4tfEPvKOdDf68JwQ3xIQ3GKLlO49MPNffmGZ61AUT72RO8vC25tNuP"

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 사용자 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        is_admin INTEGER DEFAULT 0
    )''')
    
    # 공지사항 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 고객센터(문의) 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        message TEXT,
        reply TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 관리자 계정 생성 (이메일: jokee0302@gmail.com, 비번: gogyubin1124)
    c.execute("SELECT * FROM users WHERE email='jokee0302@gmail.com'")
    if not c.fetchone():
        hashed_pw = generate_password_hash('gogyubin1124')
        c.execute("INSERT INTO users (email, password, is_admin) VALUES (?, ?, 1)", ('jokee0302@gmail.com', hashed_pw))
    
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    # 로그인 처리
    if request.method == 'POST' and 'login' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_email'] = user['email']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('index'))
        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.')
            return redirect(url_for('index'))

    # 비로그인 상태면 로그인 화면 포함된 index 렌더링
    if 'user_email' not in session:
        return render_template('index.html', notices=[], inquiries=[])

    # 로그인 상태면 DB 데이터 불러오기
    conn = get_db_connection()
    notices = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    
    if session.get('is_admin'):
        inquiries = conn.execute("SELECT * FROM inquiries ORDER BY id DESC").fetchall()
    else:
        inquiries = conn.execute("SELECT * FROM inquiries WHERE user_email=? ORDER BY id DESC", (session['user_email'],)).fetchall()
    conn.close()
    
    return render_template('index.html', notices=notices, inquiries=inquiries)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/action/notice', methods=['POST'])
def add_notice():
    if session.get('is_admin'):
        title = request.form['title']
        content = request.form['content']
        conn = get_db_connection()
        conn.execute("INSERT INTO notices (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/action/inquiry', methods=['POST'])
def add_inquiry():
    if 'user_email' in session:
        message = request.form['message']
        user_email = session['user_email']
        
        conn = get_db_connection()
        conn.execute("INSERT INTO inquiries (user_email, message) VALUES (?, ?)", (user_email, message))
        conn.commit()
        conn.close()
        
        # 디스코드 웹훅 알림
        if DISCORD_WEBHOOK_URL:
            discord_data = {
                "content": f"🚨 **새로운 고객센터 문의**\n**사용자:** {user_email}\n**내용:** {message}"
            }
            try:
                requests.post(DISCORD_WEBHOOK_URL, json=discord_data)
            except:
                pass
                
    return redirect(url_for('index'))

@app.route('/action/reply', methods=['POST'])
def add_reply():
    if session.get('is_admin'):
        inquiry_id = request.form['inquiry_id']
        reply = request.form['reply']
        conn = get_db_connection()
        conn.execute("UPDATE inquiries SET reply=? WHERE id=?", (reply, inquiry_id))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
