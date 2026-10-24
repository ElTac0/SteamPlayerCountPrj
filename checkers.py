from data_access import *
from datetime import datetime, timezone

def loadAppids(conn):
    cur = conn.execute("SELECT appid FROM Games")
    return [row[0] for row in cur.fetchall()]

def refreshGames(session, conn):
    games = fetchGames(session, pages=1)
    if games:
        saveGames(conn, games)
        print(f"refreshed game list: {len(games)} games")

def checkPlayers(session, conn):
    appids = loadAppids(conn)
    ts = datetime.now(timezone.utc).isoformat()
    rows = []
    for appid in appids:
        pc = fetchCurrentPlayers(session, appid)
        if pc is not None:
            rows.append((appid, pc))
        time.sleep(1)
    if rows:
        saveSnapshots(conn, ts, rows)
        print(f"{ts}: saved {len(rows)} player counts")

def checkPrices(session, conn):
    appids = loadAppids(conn)
    ts = datetime.now(timezone.utc).isoformat()
    prices = {}
    for i in range(0, len(appids), 100):
        prices.update(fetchPrices(session, appids[i:i+100]))
        time.sleep(1)
    if prices:
        savePrices(conn, ts, prices)
        print(f"{ts}: saved {len(prices)} prices")