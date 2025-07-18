from flask import Blueprint, render_template, request, redirect
import pyodbc
from dotenv import load_dotenv
import os
import json

load_dotenv() 

main = Blueprint('main', __name__)

try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')}"
    )
    cursor = conn.cursor()
    print("Connection successful.")
except pyodbc.Error as e:
    print("Connection failed:")
    print(e)

@main.route('/')
def show_menu():
    return "✅ App is working!"
# def show_menu():
#     cursor.execute("SELECT * FROM menuitems")
#     menu = cursor.fetchall()
#     return render_template('menu.html', menu=menu)

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
