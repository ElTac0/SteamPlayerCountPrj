import requests
from GetJson import *
import time

STEAMSPYGAMES = "https://steamspy.com/api.php"
CURRENT_PLAYERS = (
    "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
)
APPDETAILS = "https://store.steampowered.com/api/appdetails"

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