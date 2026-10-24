from data_access import *
from datetime import datetime, timezone

def loadAppids(conn):
    cur = conn.execute("SELECT appid FROM Games")
    return [row[0] for row in cur.fetchall()]

def refreshGames(session, conn):
    games = fetchGames(session, pages=1)
    for extra in (fetchSteamSpyTop(session), fetchFeatured(session), fetchMostPlayed(session)):
        for appid, name in extra.items():
            if games.get(appid) is None:   # add new games, fill missing names
                games[appid] = name
        time.sleep(1)
    saveGames(conn, games)

    # fill names for anything that came in without one
    missing = [r[0] for r in conn.execute("SELECT appid FROM Games WHERE Title IS NULL")]
    for appid in missing:
        name = fetchAppName(session, appid)
        if name:
            conn.execute("UPDATE Games SET Title=? WHERE appid=?", (name, appid))
        time.sleep(1.5)
    conn.commit()

    # recheck "free" games weekly, in case an unreleased game launched with a price
    conn.execute("UPDATE Games SET is_free=NULL WHERE is_free=1")
    conn.commit()
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
    appids = [r[0] for r in conn.execute(
        "SELECT appid FROM Games WHERE is_free IS NULL OR is_free = 0")]
    ts = datetime.now(timezone.utc).isoformat()
    prices = {}
    for i in range(0, len(appids), 100):
        prices.update(fetchPrices(session, appids[i:i+100]))
        time.sleep(1)

    # no price_overview -> free; mark it so future sweeps skip it
    conn.executemany("UPDATE Games SET is_free=? WHERE appid=?",
                     [(1 if p[0] is None else 0, appid) for appid, p in prices.items()])
    conn.commit()

    paid = {a: p for a, p in prices.items() if p[0] is not None}
    if paid:
        savePrices(conn, ts, paid)
        print(f"{ts}: saved {len(paid)} prices")