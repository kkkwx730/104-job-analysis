import os
import json
import psycopg2
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

DATA_URL = "https://media.taiwan.net.tw/XMLReleaseALL_public/scenic_spot_C_f.json"


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def clear_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM attractions;")
    conn.commit()
    cur.close()
    conn.close()


def insert_attraction(name, city, address, description, category, website):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attractions
        (name, city, address, description, category, website)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (name, city, address, description, category, website))

    conn.commit()
    cur.close()
    conn.close()


def scrape_attractions(limit=200):
    clear_table()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("正在用 Playwright 開啟官方景點資料...")
        page.goto(DATA_URL, wait_until="networkidle", timeout=60000)

        raw_text = page.locator("body").inner_text()

        if raw_text.startswith("\ufeff"):
            raw_text = raw_text.replace("\ufeff", "")

        data = json.loads(raw_text)
        attractions = data["XML_Head"]["Infos"]["Info"]

        count = 0

        for item in attractions:
            if count >= limit:
                break

            name = item.get("Name", "").strip()
            city = item.get("Region", "").strip()
            address = item.get("Add", "").strip()
            description = item.get("Description", "").strip()
            category = item.get("Class1", "").strip()
            website = item.get("Website", "").strip()

            if not name:
                continue

            if not city:
                city = "未分類"

            if not category:
                category = "一般景點"

            insert_attraction(
                name=name,
                city=city,
                address=address,
                description=description,
                category=category,
                website=website
            )

            count += 1
            print(f"已新增第 {count} 筆：{name} / {city}")

        browser.close()

    print("景點資料匯入完成！")


if __name__ == "__main__":
    scrape_attractions()