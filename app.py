from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)
app.secret_key = "your_secret_key"  # フラッシュメッセージ用

# データベースの設定
def db_config():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Passw0rd",
        db="2024sk",
    )

# データベースからt_usersとt_recordsを取得する関数
def get_users_and_records():
    conn = db_config()
    cursor = conn.cursor()
    
    # t_usersのデータ取得
    cursor.execute("SELECT * FROM t_users")
    users = cursor.fetchall()
    
    # t_recordsのデータ取得
    cursor.execute("SELECT * FROM t_records")
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return users, records

# 一番初めのページ：index.html
@app.route('/')
def index():
    users, _ = get_users_and_records()
    return render_template("index.html", data=users)

# ログインページ：login.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    users, _ = get_users_and_records()
    return render_template('login.html',data=users)

# ホーム：main.html
@app.route('/main')
def main():
    # セッションでログイン中のユーザー ID を取得（仮に user_id = 1 を固定値として使用）
    user_id = 1  # ここは適切にセッション管理を行うように改良できます

    # 今日の日付を取得
    today_date = datetime.now().strftime('%Y-%m-%d')

    # データベース接続
    conn = db_config()
    cursor = conn.cursor()

    # ユーザー情報を取得
    cursor.execute("SELECT * FROM t_users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    # 当日の体重データが存在するか確認
    cursor.execute(
        "SELECT * FROM t_records WHERE user_id = %s AND date = %s",
        (user_id, today_date)
    )
    today_record = cursor.fetchone()

    cursor.close()
    conn.close()

    # 今日の体重データがある場合とない場合のメッセージを設定
    if today_record:
        message = "今日の体重を入力しました！グラフを見て、今日も一日頑張りましょう！"
    else:
        message = "今日の体重は入力されていません。さあ、体重を測定しましょう！"

    # ユーザー名とメッセージをテンプレートに渡す
    return render_template("main.html", data=user, message=message)

# 記録確認ページ：record_confirmation.html
@app.route('/confirmation')
def confirmation():
    # データベース接続
    conn = db_config()
    cursor = conn.cursor()

    # t_usersのデータ取得
    cursor.execute("SELECT * FROM t_users")
    users = cursor.fetchall()

    # user_id = 1 の t_records のデータ取得 (新しい順に並べる)
    cursor.execute("SELECT * FROM t_records WHERE user_id = %s ORDER BY date DESC", (1,))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    # HTMLにデータを渡す
    return render_template("record_confirmation.html", data=users, records=records)


# 記録を記入するページ：input_data.html
@app.route('/input', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        # フォームデータを取得
        weight = float(request.form['weight'])
        user_id = 1  # 固定ユーザーID
        height_cm = 152.3  # 身長 (cm)
        height_m = height_cm / 100  # 身長をメートルに変換
        bmi = round(weight / (height_m ** 2), 2)  # BMI計算
        today_date = datetime.now().strftime('%Y-%m-%d')  # 当日の日付

        # データベース接続
        conn = db_config()  # データベース接続関数
        cursor = conn.cursor()

        # 前回の体重を取得
        cursor.execute("SELECT weight FROM t_records WHERE user_id = %s ORDER BY date DESC LIMIT 1", (user_id,))
        last_record = cursor.fetchone()
        weight_change = None
        if last_record:
            # decimal.Decimal を float に変換
            last_weight = float(last_record[0])
            weight_change = weight - last_weight  # 前回体重との差分

        # データ挿入
        sql = """
        INSERT INTO t_records (user_id, date, weight, weight_change, bmi)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, today_date, weight, weight_change, bmi))
        conn.commit()

        cursor.close()
        conn.close()

        flash("記録が正常に保存されました！")
        return redirect(url_for('confirmation'))  # 記録確認ページへリダイレクト

    # GETリクエスト時
    return render_template("input_data.html")

# グラフ表示ページ：display_graph.html
@app.route('/graph', methods=['GET'])
def display_graph():
    # データベース接続
    conn = db_config()
    cursor = conn.cursor()

    # t_usersのデータ取得
    cursor.execute("SELECT * FROM t_users")
    users = cursor.fetchall()

    user_ids = [1, 2]
    data = {}

    for user_id in user_ids:
        cursor.execute(
            "SELECT weight FROM t_records WHERE user_id = %s ORDER BY date ASC LIMIT 1", 
            (user_id,)
        )
        initial_weight = cursor.fetchone()[0]

        cursor.execute(
            "SELECT date, weight FROM t_records WHERE user_id = %s ORDER BY date ASC", 
            (user_id,)
        )
        records = cursor.fetchall()

        weight_changes = [
            (record[0], float(record[1]) - float(initial_weight)) for record in records
        ]
        data[user_id] = weight_changes

    cursor.close()
    conn.close()

    return render_template("display_graph.html", data=users)

# ユーザー情報(設定)：setting.html
@app.route('/setting', methods=['GET', 'POST'])
def setting():
    users, _ = get_users_and_records()
    return render_template("setting.html",data=users)


#ユーザー２のページ
# ホーム：main_friend.html
@app.route('/main_friend')
def main_friend():
    # セッションでログイン中のユーザー ID を取得（仮に user_id = 2 を固定値として使用）
    user_id = 2  # ここは適切にセッション管理を行うように改良できます

    # 今日の日付を取得
    today_date = datetime.now().strftime('%Y-%m-%d')

    # データベース接続
    conn = db_config()
    cursor = conn.cursor()

    # ユーザー情報を取得
    cursor.execute("SELECT * FROM t_users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    # 当日の体重データが存在するか確認
    cursor.execute(
        "SELECT * FROM t_records WHERE user_id = %s AND date = %s",
        (user_id, today_date)
    )
    today_record = cursor.fetchone()

    cursor.close()
    conn.close()

    # 今日の体重データがある場合とない場合のメッセージを設定
    if today_record:
        message = "今日の体重を入力しました！グラフを見て、今日も一日頑張りましょう！"
    else:
        message = "今日の体重は入力されていません。さあ、体重を測定しましょう！"

    # ユーザー名とメッセージをテンプレートに渡す
    return render_template("main_friend.html", data=user, message=message)

# 記録確認ページ：record_confirmation_friend.html
@app.route('/confirmation_friend')
def confirmation_friend():
    # データベース接続
    conn = db_config()
    cursor = conn.cursor()

    # t_usersのデータ取得
    cursor.execute("SELECT * FROM t_users")
    users = cursor.fetchall()

    # user_id = 2 の t_records のデータ取得 (新しい順に並べる)
    cursor.execute("SELECT * FROM t_records WHERE user_id = %s ORDER BY date DESC", (2,))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    # HTMLにデータを渡す
    return render_template("record_confirmation_friend.html", data=users, records=records)

# 記録を記入するページ：input_data_friend.html
# 記録を記入するページ：input_data_friend.html
@app.route('/input_friend', methods=['GET', 'POST'])
def input_data_friend():
    if request.method == 'POST':
        # フォームデータを取得
        weight = float(request.form['weight'])
        user_id = 2  # 固定ユーザーID（ユーザー2用）
        height_cm = 148.0  # 身長 (cm)
        height_m = height_cm / 100  # 身長をメートルに変換
        bmi = round(weight / (height_m ** 2), 2)  # BMI計算
        today_date = datetime.now().strftime('%Y-%m-%d')  # 当日の日付

        # データベース接続
        conn = db_config()  # データベース接続関数
        cursor = conn.cursor()

        # 前回の体重を取得
        cursor.execute("SELECT weight FROM t_records WHERE user_id = %s ORDER BY date DESC LIMIT 1", (user_id,))
        last_record = cursor.fetchone()
        weight_change = None
        if last_record:
            # decimal.Decimal を float に変換
            last_weight = float(last_record[0])
            weight_change = weight - last_weight  # 前回体重との差分

        # データ挿入
        sql = """
        INSERT INTO t_records (user_id, date, weight, weight_change, bmi)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, today_date, weight, weight_change, bmi))
        conn.commit()

        cursor.close()
        conn.close()

        flash("ユーザー2の記録が正常に保存されました！")
        return redirect(url_for('main_friend'))  # 記録確認ページではなく、ユーザー2のホームページへリダイレクト

    # GETリクエスト時
    return render_template("input_data_friend.html")

# グラフ表示ページ：display_graph_friend.html
@app.route('/graph_friend', methods=['GET'])
def display_graph_friend():
    # データベース接続
    conn = db_config()
    cursor = conn.cursor()

    # t_usersのデータ取得
    cursor.execute("SELECT * FROM t_users")
    users = cursor.fetchall()

    user_ids = [1, 2]
    data = {}

    for user_id in user_ids:
        cursor.execute(
            "SELECT weight FROM t_records WHERE user_id = %s ORDER BY date ASC LIMIT 1", 
            (user_id,)
        )
        initial_weight = cursor.fetchone()[0]

        cursor.execute(
            "SELECT date, weight FROM t_records WHERE user_id = %s ORDER BY date ASC", 
            (user_id,)
        )
        records = cursor.fetchall()

        weight_changes = [
            (record[0], float(record[1]) - float(initial_weight)) for record in records
        ]
        data[user_id] = weight_changes

    cursor.close()
    conn.close()

    return render_template("display_graph_friend.html", data=users)

# ユーザー情報(設定)：setting_friend.html
@app.route('/setting_friend', methods=['GET', 'POST'])
def setting_friend():
    users, _ = get_users_and_records()
    return render_template("setting_friend.html", data=users)

if __name__ == '__main__':
    app.run(debug=True)