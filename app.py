from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = '=abcd1234'

db_host = "localhost"
db_user = "root"
db_pass = ""
db_name = "atm_db"

def get_db_connection():
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    alert_status = None
    alert_message = None
    
    if request.method == 'POST':
        account_number = request.form['account_number']
        username = request.form['username']
        balance = float(request.form['balance'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ตรวจสอบว่า account_number มีอยู่ในฐานข้อมูลแล้วหรือไม่
        cursor.execute("SELECT account_number FROM accounts WHERE account_number = %s", (account_number,))
        existing_account = cursor.fetchone()
        
        if existing_account:
            # ถ้ามี account_number ซ้ำ
            alert_status = "fail"
            alert_message = "Account number already exists. Please choose a different account number."
        else:
            # ถ้า account_number ไม่ซ้ำ
            cursor.execute("INSERT INTO accounts (account_number, username, balance) VALUES (%s, %s, %s)", (account_number, username, balance))
            conn.commit()
            alert_status = "success"
            alert_message = "Account created successfully!"
        
        cursor.close()
        conn.close()
        
        # เก็บค่าผ่าน session
        session['alert_status'] = alert_status
        session['alert_message'] = alert_message
        return redirect(url_for('create_account'))
    
    # ส่งค่าผ่าน context
    return render_template('create_account.html', alert_status=session.get('alert_status'), alert_message=session.get('alert_message'))



@app.route('/view_balance', methods=['GET', 'POST'])
def view_balance():
    account = None
    balance = None
    if request.method == 'POST':
        account_number = request.form['account_number']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT account_number, username, balance FROM accounts WHERE account_number = %s", (account_number,))
        account = cursor.fetchone()
        if account:
            balance = account[2]
        cursor.close()
        conn.close()
        
    return render_template('view_balance.html', balance=balance, account=account)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    account = None
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        
        if amount < 100:
            session['alert_status'] = "fail"
            session['alert_message'] = "The minimum deposit amount is 100 baht."
            return redirect(url_for('index'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT account_number, username, balance FROM accounts WHERE account_number = %s", (account_number,))
        account = cursor.fetchone()
        if account:
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", (amount, account_number))
            conn.commit()
            session['alert_status'] = "success"
            session['alert_message'] = "Deposit successful!"
        else:
            session['alert_status'] = "fail"
            session['alert_message'] = "Account not found."
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('deposit.html', account=account)

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    account = None
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        
        if amount < 100:
            session['alert_status'] = "fail"
            session['alert_message'] = "The minimum withdrawal amount is 100 baht."
            return redirect(url_for('index'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT account_number, username, balance FROM accounts WHERE account_number = %s", (account_number,))
        account = cursor.fetchone()
        
        if account:
            if account[2] >= amount:
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
                conn.commit()
                session['alert_status'] = "success"
                session['alert_message'] = "Withdrawal successful!"
            else:
                session['alert_status'] = "fail"
                session['alert_message'] = "You have insufficient funds in your account."
        else:
            session['alert_status'] = "fail"
            session['alert_message'] = "Account not found."
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('withdraw.html', account=account)

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    account = None
    if request.method == 'POST':
        account_number = request.form['account_number']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT account_number, username, balance FROM accounts WHERE account_number = %s", (account_number,))
        account = cursor.fetchone()
        
        if account:
            cursor.execute("DELETE FROM accounts WHERE account_number = %s", (account_number,))
            conn.commit()
            session['alert_status'] = "success"
            session['alert_message'] = "Account deleted successfully!"
        else:
            session['alert_status'] = "fail"
            session['alert_message'] = "Account not found."
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('index'))
    
    
    return render_template('delete_account.html', account=account)

if __name__ == '__main__':
    app.run(debug=True)