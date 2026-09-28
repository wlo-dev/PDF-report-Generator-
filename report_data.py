import sqlite3

DB_PATH = "report.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_report_data():
    conn = get_connection()

    total_orders = conn.execute("SELECT COUNT(*) AS n FROM orders").fetchone()["n"]

    total_revenue = conn.execute("SELECT SUM(amount) AS total FROM orders").fetchone()["total"]

    top_products = conn.execute("""
        SELECT product, SUM(amount) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
    """).fetchall()

    orders_per_day = conn.execute("""
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM orders
        WHERE DATE(created_at) >= DATE('now', '-6 days')
        GROUP BY day
        ORDER BY day
    """).fetchall()

    all_orders = conn.execute(
        "SELECT customer, product, amount, created_at FROM orders ORDER BY created_at DESC"
    ).fetchall()

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2) if total_revenue else 0,
        "top_products": [dict(row) for row in top_products],
        "orders_per_day": [dict(row) for row in orders_per_day],
        "all_orders": [dict(row) for row in all_orders],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_report_data(), indent=2))