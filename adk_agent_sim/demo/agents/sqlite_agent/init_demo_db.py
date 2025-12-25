import os
import sqlite3

# Ensure this matches the path defined in your agent.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "test.db")


def init_db():
  # Delete existing DB to ensure a clean state for "Golden Traces"
  if os.path.exists(DB_PATH):
    try:
      os.remove(DB_PATH)
      print(f"🗑️  Removed old {DB_PATH}")
    except PermissionError:
      print(
        f"⚠️  Could not remove {DB_PATH} (might be in use). Overwriting tables instead."
      )

  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  print("🛠️  Initializing database schema...")

  # 1. Products Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        )
    """)

  # 2. Customers Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """)

  # 3. Orders Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

  # 4. Order Items Table (Junction)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

  print("🌱  Seeding mock data...")

  # Insert Products
  products = [
    (1, "Laptop Pro", "Electronics", 1200.00, 50),
    (2, "Wireless Mouse", "Accessories", 25.50, 200),
    (3, "Mechanical Keyboard", "Accessories", 85.00, 0),  # EDGE CASE: Out of stock
    (4, "USB-C Cable", "Accessories", 12.00, 100),
    (5, "Monitor 4K", "Electronics", 450.00, 15),
  ]
  cursor.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)

  # Insert Customers
  customers = [
    (1, "Alice Engineer", "alice@example.com", "vip"),
    (2, "Bob Manager", "bob@example.com", "active"),
    (3, "Charlie Newbie", "charlie@example.com", "pending"),  # EDGE CASE: No orders
  ]
  cursor.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)

  # Insert Orders
  orders = [
    (101, 1, "2023-10-01", "shipped"),  # Alice bought stuff
    (102, 1, "2023-10-15", "processing"),  # Alice bought more stuff
    (103, 2, "2023-10-05", "delivered"),  # Bob bought stuff
  ]
  cursor.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)

  # Insert Order Items
  order_items = [
    (1, 101, 1, 1),  # Alice bought 1 Laptop
    (2, 101, 2, 2),  # Alice bought 2 Mice
    (3, 102, 5, 1),  # Alice bought 1 Monitor
    (4, 103, 4, 5),  # Bob bought 5 Cables
  ]
  cursor.executemany("INSERT INTO order_items VALUES (?,?,?,?)", order_items)

  conn.commit()
  conn.close()
  print(f"✅  Database initialized at: {os.path.abspath(DB_PATH)}")


if __name__ == "__main__":
  init_db()
