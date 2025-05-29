from flask import Flask, jsonify, request
import psycopg2
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = Flask(__name__)



@app.route('/api')
def hello():
    return "API Root Tickle Tickle you're almost there!"

# --- DB CHECK ---
@app.route('/db-check')
def db_check():
    return "DB check passed"





# --- GET USERS ---
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        users = [dict(zip(column_names, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- POST USERS ---
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']

        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id", (name, email))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": user_id, "name": name, "email": email}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- POST PRODUCTS ---
@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        name = data['name']
        price = data['price']

        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price, created_at) VALUES (%s, %s, NOW()) RETURNING id", (name, price))
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": product_id, "name": name, "price": price}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
# --- GET PRODUCTS ---
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        products = [dict(zip(column_names, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- PUT PRODUCTS ---
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        name = data['name']
        price = data['price']

        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("UPDATE products SET name = %s, price = %s WHERE id = %s", (name, price, product_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Product updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- DELETE PRODUCTS ---
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Product deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- GET PRODUCT BY ID ---
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        row = cur.fetchone()
        if row:
            column_names = [desc[0] for desc in cur.description]
            product = dict(zip(column_names, row))
        else:
            product = None
        cur.close()
        conn.close()
        if product:
            return jsonify(product)
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# --- POST ORDERS ---
@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        user_id = data['user_id']
        product_id = data['product_id']
        quantity = data['quantity']

        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, product_id, quantity))
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": order_id, "user_id": user_id, "product_id": product_id, "quantity": quantity}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- GET ORDERS ---
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        orders = [dict(zip(column_names, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- GET ORDER BY ID ---
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Order not found"}), 404
        column_names = [desc[0] for desc in cur.description]
        order = dict(zip(column_names, row))
        cur.close()
        conn.close()
        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- PUT ORDER ---
@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.get_json()
        user_id = data['user_id']
        product_id = data['product_id']
        quantity = data['quantity']

        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("UPDATE orders SET user_id = %s, product_id = %s, quantity = %s WHERE id = %s",
                    (user_id, product_id, quantity, order_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Order updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- DELETE ORDER ---
@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Order deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# --- APP RUN ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
