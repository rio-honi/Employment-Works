from flask import Flask
from flask import render_template

app = Flask(__name__)

#一番初めのページ：index.html
@app.route('/')
def index():
    return render_template("index.html")

#ログインページ：login.html
@app.route('/login')
def login():
    return render_template("login.html")

#ユーザー登録するページ：register.html
@app.route('/register')
def register():
    return render_template("register.html")

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
