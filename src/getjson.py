import time
import requests

def getJson(session,url,params=None,tries=3):
    for attempt in range(tries):
        try:
            response = session.get(url,params=params,timeout=20)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429 or response.status_code>=500:
                time.sleep(2 ** attempt)
                continue
            return None
        except (requests.RequestException, ValueError):
            time.sleep(2 ** attempt)
    return None