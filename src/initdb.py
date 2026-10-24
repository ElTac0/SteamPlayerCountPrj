import os
import sqlite3

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "steam.db")

def initDB():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Games(
        appid INTEGER PRIMARY KEY,
        title TEXT,
        is_free INTEGER)""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS PlayerCounts(
        time_snapshot TEXT,
        appid INTEGER,
        player_count INTEGER,
        PRIMARY KEY(appid, time_snapshot))""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS PriceSnapshots(
        time_snapshot TEXT,
        appid INTEGER,
        initial INTEGER,
        final INTEGER,
        discount_percent INTEGER,
        on_sale INTEGER,
        PRIMARY KEY(appid, time_snapshot))""")
    
    conn.commit()
    return conn