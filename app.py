from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join("data", "board.db")

def init_db():
    # data 폴더 없으면 생성
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# 서버 시작할 때 DB 초기화
init_db()

@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at FROM posts ORDER BY id DESC")
    posts = cur.fetchall()
    conn.close()
    return render_template("index.html", posts=posts)

@app.route("/post/<int:id>")
def detail(id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM posts WHERE id = ?", (id,))
    post = cur.fetchone()
    conn.close()
    if not post:
        return "Not Found", 404
    return render_template("detail.html", post=post)

@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            return "제목과 내용을 입력해야 합니다.", 400

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("new.html")

@app.route("/health")
def health():
    # 최소 체크: DB 파일이 있는지만 간단히 확인
    db_exists = os.path.exists(DB_PATH)
    status = {
        "status": "ok",
        "db": "ok" if db_exists else "missing"
    }
    return status, 200


# 404 에러 핸들러
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# 500 에러 핸들러
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    # 개발용 서버 실행
    app.run(host="0.0.0.0", port=8000, debug=True)


