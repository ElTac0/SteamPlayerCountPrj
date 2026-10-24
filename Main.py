import time
import requests
from initdb import *
from data_access import *
from checkers import *

DB_PATH = "Data/steam.db"

def main():
    session = requests.Session()
    conn = initDB()

    REFRESH_INTERVAL = 7 * 24 * 3600   # weekly
    PLAYER_INTERVAL = 5 * 3600
    PRICE_INTERVAL = 24 * 3600

    next_refresh = 0
    next_players = 0
    next_prices = 0

    while True:
        now = time.time()
        if now >= next_refresh:
            refreshGames(session, conn)
            next_refresh = now + REFRESH_INTERVAL
        if now >= next_players:
            checkPlayers(session, conn)
            next_players = now + PLAYER_INTERVAL
        if now >= next_prices:
            checkPrices(session, conn)
            next_prices = now + PRICE_INTERVAL
        time.sleep(600)
        


if __name__ == "__main__":
    main()