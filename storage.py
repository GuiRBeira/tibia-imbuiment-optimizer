import sqlite3
from datetime import datetime
from typing import Dict, Optional

DB_PATH = "prices.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            world TEXT NOT NULL,
            item_name TEXT NOT NULL,
            price INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_prices(world: str, gold_token_price: int, material_prices: Dict[str, int]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO prices (timestamp, world, item_name, price) VALUES (?, ?, ?, ?)",
        (timestamp, world, "Gold Token", gold_token_price)
    )
    
    for mat_name, price in material_prices.items():
        cursor.execute(
            "INSERT INTO prices (timestamp, world, item_name, price) VALUES (?, ?, ?, ?)",
            (timestamp, world, mat_name, price)
        )
        
    conn.commit()
    conn.close()

def get_latest_prices(world: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT item_name, price
        FROM prices
        WHERE world = ? AND timestamp = (
            SELECT MAX(timestamp) FROM prices WHERE world = ?
        )
    """, (world, world))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None
        
    material_prices = {}
    gold_token_price = 0
    for item_name, price in rows:
        if item_name == "Gold Token":
            gold_token_price = price
        else:
            material_prices[item_name] = price
            
    return gold_token_price, material_prices

def get_average_price_last_days(world: str, item_name: str, days: int = 7) -> Optional[float]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(price)
        FROM prices
        WHERE world = ?
        AND item_name = ?
        AND timestamp > datetime('now', ?)
    """, (world, item_name, f'-{days} days'))
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else None