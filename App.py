from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Data store setup
ORDERS_FILE = 'orders.json'
MENU_FILE = 'menu.json'

# Initialize files for the app
def init_files():
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(MENU_FILE):
        menu_data = [
            {"id": 1, "name": "Steam Momos", "price": 50, "description": "Delicious steamed momos with veg filling."},
            {"id": 2, "name": "Fried Momos", "price": 60, "description": "Crispy fried momos with veg filling."},
            {"id": 3, "name": "Pan Fried Momos", "price": 70, "description": "Tasty pan-fried momos."},
            {"id": 4, "name": "Momos with Chutney", "price": 10, "description": "Extra spicy chutney."}
        ]
        with open(MENU_FILE, 'w') as f:
            json.dump(menu_data, f)

init_files()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/menu')
def get_menu():
    with open(MENU_FILE, 'r') as f:
        menu = json.load(f)
    return jsonify(menu)

@app.route('/api/order', methods=['POST'])
def place_order():
    try:
        data = request.get_json()
        customer_name = data.get('customer_name')
        customer_phone = data.get('customer_phone')
        items = data.get('items', [])

        # Calculate total amount
        total = 0
        with open(MENU_FILE, 'r') as f:
            menu = json.load(f)
        menu_dict = {item['id']: item for item in menu}
        for item in items:
            menu_item = menu_dict.get(item['id'])
            if menu_item:
                total += menu_item['price'] * item['quantity']

        # Check ₹200 limit
        if total > 200:
            return jsonify({"success": False, "error": "Order total exceeds the ₹200 limit."}), 400

        # Create new order
        with open(ORDERS_FILE, 'r') as f:
            orders = json.load(f)
        new_order = {
            "id": len(orders) + 1,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "items": items,
            "total": total,
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        }
        orders.append(new_order)
        with open(ORDERS_FILE, 'w') as f:
            json.dump(orders, f, indent=4)

        # Generate UPI Payment Link (UPDATED UPI ID: 7428733852-2@ybl)
        upi_id = "7428733852-2@ybl" 
        payment_link = f"upi://pay?pa={upi_id}&pn=Evening Drop Momos&am={total}&cu=INR&tn=Order{new_order['id']}"

        return jsonify({
            "success": True,
            "order_id": new_order['id'],
            "total": total,
            "payment_link": payment_link
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
