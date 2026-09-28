import random
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "report.db"
PRODUCTS = ["Widget", "Gadget", "Doohickey", "Gizmo", "Thingamajig", "Contraption"]
CUSTOMERS = ["Ada Lovelace", "Grace Hopper", "Alan Turing", "Katherine Johnson", "Vint Cerf"]
NUM_ORDERS = 200

conn = sqlite3.connect(DB_PATH)

conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT NOT NULL,
        product TEXT NOT NULL,
        amount REAL NOT NULL,
        created_at TEXT NOT NULL
    )
""")

conn.execute("DELETE FROM orders")

now = datetime.now()
rows = []
for _ in range(NUM_ORDERS):
    customer = random.choice(CUSTOMERS)
    product = random.choice(PRODUCTS)
    amount = round(random.uniform(5, 200), 2)
    days_ago = random.randint(0, 29)
    created_at = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
    rows.append((customer, product, amount, created_at))

conn.executemany(
    "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
    rows,
)

conn.commit()
conn.close()

print("Seeded report.db")