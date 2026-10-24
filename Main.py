import sys
import time
import sqlite3
from datetime import datetime, timezone
import requests
from InitDB import *
from Fetchers import *
from Savers import *

DB_PATH = "Data/steam.db"

LIMIT = 10   # set to None for the full run

def main():
    print("Starting Steam player count snapshot...")
    session = requests.Session()
    conn = initDB()
    games = fetchGames(session, pages=1)
    if not games:
        sys.exit(1)
    saveGames(conn, games)

    appids = list(games)
    if LIMIT:
        appids = appids[:LIMIT]

    ts = datetime.now(timezone.utc).isoformat()
    rows = []
    for appid in appids:
        playerCount = fetchCurrentPlayers(session, appid)
        if playerCount is not None:
            rows.append((appid, playerCount))
        time.sleep(1)

    if not rows:
        sys.exit(1)
    saveSnapshots(conn, ts, rows)
    print(f"{ts}: saved {len(rows)} games")

    prices = {}
    for i in range(0, len(appids), 100):
        batch = appids[i:i + 100]
        prices.update(fetchPrices(session, batch))
        time.sleep(1)
    if prices:
        savePrices(conn, ts, prices)
        print(f"{ts}: saved {len(prices)} prices")

    conn.close()