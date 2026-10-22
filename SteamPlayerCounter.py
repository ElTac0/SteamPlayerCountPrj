import sys
import time
import sqlite3
from datetime import datetime, timezone
import requests

DB_PATH = "/data/steam.db"
STEAMSPYGAMES = "https://steamspy.com/api.php"
CURRENT_PLAYERS = (
    "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
)
APPDETAILS = "https://store.steampowered.com/api/appdetails"
HEADERS = {"User-Agent": "panel-discovery/1.0"}

def initDb(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            appid INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            appid INTEGER,
            player_count INTEGER
        )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS price_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        appid INTEGER,
        initial_cents INTEGER,
        final_cents INTEGER,
        discount_percent INTEGER,
        on_sale INTEGER
    )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_price ON price_snapshots(appid, ts)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_snap ON snapshots(appid, ts)")
    conn.commit()
    return conn

def fetchPrices(session, appids):
    """Return {appid: (initial, final, discount_pct, on_sale)} for a batch."""
    ids = ",".join(str(a) for a in appids)
    data = getJson(session, APPDETAILS,
                   params={"appids": ids, "filters": "price_overview"})
    if not data:
        return {}
    out = {}
    for appid_str, entry in data.items():
        appid = int(appid_str)
        if not entry.get("success"):
            continue
        price = (entry.get("data") or {}).get("price_overview")
        if not price:          # free game or no price -> record as not on sale
            out[appid] = (None, None, 0, 0)
            continue
        disc = price.get("discount_percent", 0)
        out[appid] = (
            price.get("initial"),
            price.get("final"),
            disc,
            1 if disc > 0 else 0,
        )
    return out

def savePrices(conn, ts, price_map):
    conn.executemany(
        "INSERT INTO price_snapshots "
        "(ts, appid, initial_cents, final_cents, discount_percent, on_sale) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(ts, appid, i, f, d, s) for appid, (i, f, d, s) in price_map.items()]
    )
    conn.commit()

def saveGames(conn, games):
    conn.executemany(
        "INSERT INTO games (appid, name) VALUES (?, ?) "
        "ON CONFLICT(appid) DO UPDATE SET name=excluded.name",
        list(games.items())
    )
    conn.commit()

def saveSnapshots(conn, ts, rows):
    conn.executemany(
        "INSERT INTO snapshots (ts, appid, player_count) VALUES (?, ?, ?)",
        [(ts, appid, pc) for appid, pc in rows]
    )
    conn.commit()

def getJson(session, url, params=None, tries=3):
    for attempt in range(tries):
        try:
            response = session.get(url, params=params, headers=HEADERS, timeout=20)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429 or response.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            return None
        except (requests.RequestException, ValueError):
            time.sleep(2 ** attempt)
    return None

def fetchGames(session, pages):
    games = {}
    for page in range(pages):
        if page > 0:
            print(f" waiting 60s before SteamSpy page {page} (rate limit)...")
            time.sleep(60)
        data = getJson(session, STEAMSPYGAMES, params={"request": "all", "page": page})
        if not data:
            print(f" page {page}: request failed, skipping")
            continue    
        for appid, info in data.items():
            try:
                appid_int = int(appid)
            except (TypeError, ValueError):
                continue
            games[appid_int] = (info or {}).get("name", f"app {appid_int}")
    return games

def fetchCurrentPlayers(session, appid):
    data = getJson(session, CURRENT_PLAYERS, params={"appid": appid})
    if not data:
        return None
    response = data.get("response",{})
    if response.get("result") != 1:
        return None
    return response.get("player_count")

def main():
    print("Starting Steam player count snapshot...")
    session = requests.Session()
    conn = initDb()
    games = fetchGames(session, pages=1)
    if not games:
        sys.exit(1)
    saveGames(conn, games)

    ts = datetime.now(timezone.utc).isoformat()
    rows = []
    for appid in games:
        playerCount = fetchCurrentPlayers(session, appid)
        if playerCount is not None:
            rows.append((appid, playerCount))
        time.sleep(1)

    if not rows:
        sys.exit(1)
    saveSnapshots(conn, ts, rows)
    print(f"{ts}: saved {len(rows)} games")

    prices = {}
    appids = list(games)
    for i in range(0, len(appids), 100):
        batch = appids[i:i + 100]
        prices.update(fetchPrices(session, batch))
        time.sleep(1)
    if prices:
        savePrices(conn, ts, prices)
        print(f"{ts}: saved {len(prices)} prices")

    conn.close()

if __name__ == "__main__":
    main()   