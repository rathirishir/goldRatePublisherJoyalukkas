import os
import time
import requests
from datetime import datetime

GRAPHQL_URL = "https://www.joyalukkas.in/graphql?query=query+getgoldrates%7Bgetgoldrates%7BId+Message+Status+metal_rate_time+Data%7BId+BRANCH_CODE+BRANCH_NAME+GOLD_14KT_RATE+GOLD_18KT_RATE+GOLD_22KT_RATE+GOLD_24KT_RATE+SILVER_RATE+SILVER_RATE100+SILVER_RATE999+PLATINUM_RATE+__typename%7D__typename%7D%7D&operationName=getgoldrates&variables=%7B%7D"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Referer": "https://www.joyalukkas.in/",
    "content-type": "application/json",
    "x-channel-id": "WEB",
    "x-platform": "WEB",
    "x-device-type": "Desktop",
    "x-app-version": "0.0.1",
    "store": "default",
}

CHECK_INTERVAL_SECONDS = 4 * 60 * 60

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def fetch_gold_rate():
    r = requests.get(GRAPHQL_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()

    rate_block = data["data"]["getgoldrates"]
    rows = rate_block.get("Data", [])
    if not rows:
        raise ValueError("No gold rate rows returned")

    row = rows[0]
    rate = row["GOLD_22KT_RATE"]
    branch = row.get("BRANCH_NAME", "Unknown")
    ts = rate_block.get("metal_rate_time", "")

    return rate, branch, ts


def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run_once():
    try:
        rate, branch, ts = fetch_gold_rate()
        msg = f"Joyalukkas India 22K gold rate: ₹{rate} per gram\nBranch: {branch}\nRate time: {ts}\nChecked at: {datetime.now():%Y-%m-%d %H:%M:%S}"
        send_telegram_message(msg)
        print(msg)
    except Exception as e:
        err = f"Joyalukkas gold alert failed: {e}"
        print(err)
        try:
            send_telegram_message(err)
        except Exception:
            pass


def main():
    while True:
        run_once()
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
