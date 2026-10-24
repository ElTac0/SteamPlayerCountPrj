def saveGames(conn, games):
    conn.executemany(
        "INSERT INTO Games (appid, Title) VALUES (?, ?) "
        "ON CONFLICT(appid) DO UPDATE SET Title=excluded.Title",
        list(games.items())
    )
    conn.commit()

def saveSnapshots(conn, ts, rows):
    conn.executemany(
        "INSERT INTO PlayerCounts (time_snapshot, appid, player_count) VALUES (?, ?, ?)",
        [(ts, appid, pc) for appid, pc in rows]
    )
    conn.commit()

def savePrices(conn, ts, price_map):
    conn.executemany(
        "INSERT INTO PriceSnapshots "
        "(time_snapshot, appid, initial, final, discount_percent, on_sale) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(ts, appid, i, f, d, s) for appid, (i, f, d, s) in price_map.items()]
    )
    conn.commit()