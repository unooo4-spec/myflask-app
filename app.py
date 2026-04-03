import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            unit_price INTEGER NOT NULL,
            total INTEGER NOT NULL,
            purchase_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add", methods=["POST"])
def add():
    init_db()

    item_name = request.form["item_name"]
    quantity = int(request.form["quantity"])
    unit = request.form["unit"]
    unit_price = int(request.form["unit_price"])
    purchase_date = request.form["purchase_date"]
    total = quantity * unit_price

    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO purchases (item_name, quantity, unit, unit_price, total, purchase_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (item_name, quantity, unit, unit_price, total, purchase_date))

    conn.commit()
    conn.close()

    return redirect("/list")


@app.route("/list")
def list_page():
    init_db()

    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM purchases ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()

    return render_template("list.html", data=data)


@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM purchases WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/list")


@app.route("/history")
def history():
    init_db()

    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT
            item_name,
            SUM(quantity) AS total_quantity,
            SUM(total) AS total_amount
        FROM purchases
        GROUP BY item_name
        ORDER BY item_name
    """)

    data = cur.fetchall()
    conn.close()

    return render_template("history.html", data=data)


@app.route("/monthly")
def monthly():
    init_db()

    selected_month = request.args.get("month", "")

    conn = sqlite3.connect("stock.db")
    cur = conn.cursor()

    if selected_month:
        cur.execute("""
            SELECT item_name, SUM(quantity), SUM(total)
            FROM purchases
            WHERE substr(purchase_date, 1, 7) = ?
            GROUP BY item_name
        """, (selected_month,))
    else:
        cur.execute("""
            SELECT item_name, SUM(quantity), SUM(total)
            FROM purchases
            GROUP BY item_name
        """)

    data = cur.fetchall()
    conn.close()

    return render_template("monthly.html", data=data, selected_month=selected_month)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
