import os
import sqlite3

path = "Data/steam.db"

def initDB():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Games(
        appid INTEGER PRIMARY KEY,
        Title TEXT)""")
    
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