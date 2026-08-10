import os
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

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def fetch_gold_rate():
    r = requests.get(GRAPHQL_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    payload = r.json()

    block = payload["data"]["getgoldrates"]
    rows = block.get("Data", [])
    if not rows:
        raise ValueError("No gold rate rows returned")

    row = rows[0]
    return {
        "rate": row["GOLD_22KT_RATE"],
        "branch": row.get("BRANCH_NAME", "Unknown"),
        "rate_time": block.get("metal_rate_time", ""),
    }


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    result = fetch_gold_rate()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (
        f"Joyalukkas India 22K gold rate: <b>₹{result['rate']}</b> per gram\n"
        f"Branch: {result['branch']}\n"
        f"Rate time: {result['rate_time']}\n"
        f"Checked at: {now}"
    )
    send_telegram_message(msg)
    print(msg)


if __name__ == "__main__":
    main()
