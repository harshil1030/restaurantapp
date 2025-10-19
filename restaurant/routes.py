from flask import flash
import random
from flask import Blueprint, app, render_template, request, redirect, session, url_for, flash
import pyodbc
from dotenv import load_dotenv
import os
import json
import pytds
import os
from flask import jsonify

from .otpservice import generate_otp, send_otp, store_otp
from .otpservice import verify_otp as check_otp
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
    order_data = request.form['order_data']  # JSON string of order items
    
    if not mobile_number.startswith('+91'):
        mobile_number = '+91' + mobile_number
    
    # Save temporarily in session
    session['pending_order'] = order_data
    session['mobile_number'] = mobile_number

    # Generate + send OTP
    otp = generate_otp()
    store_otp(mobile_number, otp)
    sent = send_otp(mobile_number, otp)
    
    if sent:
        return jsonify({"success": True, "message": "OTP sent successfully!"})
    else:
        return jsonify({"success": False, "message": "Failed to send OTP"}), 500

    # if sent:
    #     flash("OTP sent successfully! Please verify.")
    # else:
    #     flash("Failed to send OTP. Please try again.")
    #     return redirect(url_for('main.show_menu'))
    # return redirect(url_for('main.verify_otp'))


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


@main.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        mobile_number = session.get('mobile_number')

        is_valid, msg = check_otp(mobile_number, user_otp)
        if is_valid:
            # Insert order into DB
            order_data = session.get('pending_order')
            items = json.loads(order_data)
            for item_id, item in items.items():
                cursor.execute(
                    "INSERT INTO Orders (mobile_number, item_id, name, qty, status) VALUES (?, ?, ?, ?, ?)",
                    (mobile_number, item_id, item['name'], item['qty'], 'pending')
                )
            conn.commit()

            # Clear session
            session.pop('otp', None)
            session.pop('pending_order', None)
            session.pop('mobile_number', None)

            flash("✅ Order placed successfully!")
            return redirect(url_for('main.show_menu'))
        else:
            flash(f"Invalid OTP: {msg}")
            return redirect(url_for('main.verify-otp'))

    return render_template('verify-otp.html')