from flask import flash
import random
from flask import Blueprint, app, render_template, request, redirect, session, url_for, flash
import pyodbc
from dotenv import load_dotenv
import os
import json
import pytds
import os
from twilio.rest import Client
import os

load_dotenv() 

main = Blueprint('main', __name__)


conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

@main.route('/')
def show_menu():
    cursor.execute("SELECT * FROM menuitems")
    menu = cursor.fetchall()
    return render_template('menu.html', menu=menu)

@main.route('/place_order', methods=['POST'])
def place_order():
    mobile_number = request.form['mobile_number']
    order_data = request.form['order_data']
    items = json.loads(order_data)

    for item_id, item in items.items():
        name = item['name']
        qty = item['qty']

        cursor.execute(
            "INSERT INTO Orders (mobile_number, item_id, name, qty) VALUES (?, ?, ?, ?)",
            (mobile_number, item_id, name, qty)
        )

    conn.commit()
    return redirect('/')



@main.route('/kitchen')
def kitchen():
    cursor.execute("""
        SELECT id, name, qty, mobile_number, order_time, status, priority
        FROM Orders
        WHERE status = 'pending'
        ORDER BY priority DESC, order_time ASC
    """)
    orders = cursor.fetchall()
    return render_template("kitchen.html", orders=orders)


@main.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    cursor.execute("UPDATE Orders SET status = 'ready' WHERE id = ?", (order_id,))
    conn.commit()
    return redirect('/kitchen')

@main.route('/send-otp', methods=['GET', 'POST'])
def send_otp():
    if request.method == 'POST':
        mobile_number = request.form['mobile_number']
        otp = str(random.randint(100000, 999999))
        session['otp'] = otp
        session['mobile_number'] = mobile_number

        # Send OTP using Twilio
        client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH"))
        client.messages.create(
            body=f"Your OTP is {otp}",
            from_=os.getenv("TWILIO_FROM"),
            to=mobile_number
        )

        flash("OTP sent successfully!")
        return redirect(url_for('verify_otp'))

    return render_template('send_otp.html')

@main.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session.get('otp'):
            flash("OTP Verified Successfully!")
            return redirect('/')
        else:
            flash("Invalid OTP. Try again.")
            return redirect(url_for('verify_otp'))

    return render_template('verify_otp.html')