import sqlite3
from datetime import datetime
from typing import Dict, Optional, Tuple

DB_PATH = "prices.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fazemos um PRAMGA para checar se a tabela existe e quais são as colunas
    cursor.execute("PRAGMA table_info(prices)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if columns:
        if "price" in columns and "instant_price" not in columns:
            # Migration do MVP v1 para v2
            cursor.execute("ALTER TABLE prices RENAME COLUMN price TO instant_price")
            cursor.execute("ALTER TABLE prices ADD COLUMN order_price INTEGER DEFAULT 0")
    else:
        cursor.execute("""
            CREATE TABLE prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                world TEXT NOT NULL,
                item_name TEXT NOT NULL,
                instant_price INTEGER NOT NULL,
                order_price INTEGER NOT NULL
            )
        """)
        
    conn.commit()
    conn.close()

def save_prices(world: str, gold_token_prices: Tuple[int, int], material_prices: Dict[str, Tuple[int, int]]):
    # Tuple[int, int] representa (instant_price, order_price)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO prices (timestamp, world, item_name, instant_price, order_price) VALUES (?, ?, ?, ?, ?)",
        (timestamp, world, "Gold Token", gold_token_prices[0], gold_token_prices[1])
    )
    
    for mat_name, (inst_price, ord_price) in material_prices.items():
        cursor.execute(
            "INSERT INTO prices (timestamp, world, item_name, instant_price, order_price) VALUES (?, ?, ?, ?, ?)",
            (timestamp, world, mat_name, inst_price, ord_price)
        )
        
    conn.commit()
    conn.close()

def get_average_prices_last_days(world: str, item_name: str, days: int = 7) -> Optional[Tuple[float, float]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(instant_price), AVG(order_price)
        FROM prices
        WHERE world = ?
        AND item_name = ?
        AND timestamp > datetime('now', ?)
    """, (world, item_name, f'-{days} days'))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] is not None:
        return row[0], row[1]
    return None

def get_daily_average_prices(world: str, item_name: str, days: int = 7) -> Dict[str, Tuple[float, float]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date(timestamp) as day, AVG(instant_price), AVG(order_price)
        FROM prices
        WHERE world = ? AND item_name = ?
        AND timestamp > datetime('now', ?)
        GROUP BY day
        ORDER BY day ASC
    """, (world, item_name, f'-{days} days'))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: (row[1], row[2]) for row in rows}