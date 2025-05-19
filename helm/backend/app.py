from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

@app.route('/api')
def hello():
    return "API Root"

@app.route('/api/items', methods=['GET'])
def get_items():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            dbname='postgres'  # Replace if using a different DB
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM items")
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        items = [dict(zip(column_names, row)) for row in rows]
        cur.close()
        conn.close()
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/db-check')
def db_check():
    return "DB check passed"

# ✅ ADD THIS PART:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
