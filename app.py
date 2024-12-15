from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import os
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # フラッシュメッセージ用

#データベースの設定
def db_config():
    conn = mysql.connector.connect(
        host = "127.0.0.1",
        user = "root",
        password = "Passw0rd",
        db = "2024sk",        
    )
    return conn

#データベースの接続
conn = db_config()
#データベースの操作用変数定義
cursor = conn.cursor()

sql = "select * from t_users"
#SQLの実行
cursor.execute(sql)
#データの取り出し
data = cursor.fetchall()
#出力
print(data)

#データベース接続の初期化
#db = SQLAlchemy(app)

#一番初めのページ：index.html
@app.route('/')
def index():
    return render_template("index.html" ,data = data)

#ログインページ：login.html
@app.route('/login')
def login():
    return render_template("login.html")

#ユーザー登録するページ：register.html
@app.route('/register', methods=['GET', 'POST'])
def register():    
    return render_template('register.html')

#ホーム：main.html
@app.route('/main')
def home():
    return render_template("main.html")

#記録確認ページ：record_confirmation.html
@app.route('/confirmation')
def confirmation():
    return render_template("record_confirmation.html")

#記録を記入するページ：input_data.html
@app.route('/input')
def imput():
    return render_template("input_data.html")

#グラフ表示ページ：display_graph.html
@app.route('/graph')
def graph():
    return render_template("display_graph.html")

#ユーザー情報(設定)：setting.html
@app.route('/setting')
def setting():
    return render_template("setting.html")


if __name__ == '__main__':
    app.run(debug=True)
