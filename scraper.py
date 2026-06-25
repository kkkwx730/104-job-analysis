import os
import json
import psycopg2
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATA_URL = "https://media.taiwan.net.tw/XMLReleaseALL_public/scenic_spot_C_f.json"

CITY_LIMITS = {
    "桃園市": 14,
    "新北市": 18,
    "臺北市": 12,
    "臺中市": 16,
    "臺南市": 15,
    "高雄市": 17,
    "宜蘭縣": 10,
    "花蓮縣": 13,
    "臺東縣": 11,
    "金門縣": 20
}

CATEGORY_MAP = {
    "1": "自然景觀",
    "2": "人文歷史",
    "3": "古蹟文化",
    "4": "宗教景點",
    "5": "休閒娛樂",
    "6": "觀光工廠",
    "7": "生態教育",
    "8": "藝術文化",
    "9": "地方特色",
    "10": "國家風景區",
    "11": "博物館",
    "12": "老街商圈",
    "13": "溫泉",
    "14": "遊憩園區",
    "15": "親子景點",
    "16": "美食購物",
    "17": "戶外步道",
    "18": "其他景點"
}


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


def safe_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_city(region, address):
    text = f"{region} {address}"

    city_alias = {
        "桃園": "桃園市",
        "新北": "新北市",
        "台北": "臺北市",
        "臺北": "臺北市",
        "台中": "臺中市",
        "臺中": "臺中市",
        "台南": "臺南市",
        "臺南": "臺南市",
        "高雄": "高雄市",
        "宜蘭": "宜蘭縣",
        "花蓮": "花蓮縣",
        "台東": "臺東縣",
        "臺東": "臺東縣",
        "金門": "金門縣"
    }

    for key, value in city_alias.items():
        if key in text:
            return value

    return safe_text(region)


def get_category(code):
    code = safe_text(code).lstrip("0")
    return CATEGORY_MAP.get(code, "其他景點")


def scrape_attractions():
    clear_table()

    city_counts = {city: 0 for city in CITY_LIMITS.keys()}

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

        total_count = 0

        for item in attractions:
            name = safe_text(item.get("Name"))
            region = safe_text(item.get("Region"))
            address = safe_text(item.get("Add"))
            description = safe_text(item.get("Description"))
            website = safe_text(item.get("Website"))

            city = normalize_city(region, address)

            if not name:
                continue

            if city not in CITY_LIMITS:
                continue

            if city_counts[city] >= CITY_LIMITS[city]:
                continue

            category = get_category(item.get("Class1"))

            insert_attraction(
                name=name,
                city=city,
                address=address,
                description=description,
                category=category,
                website=website
            )

            city_counts[city] += 1
            total_count += 1

            print(f"已新增第 {total_count} 筆：{name} / {city} / {category}")

            if all(city_counts[city] >= CITY_LIMITS[city] for city in CITY_LIMITS):
                break

        browser.close()

    print("景點資料匯入完成！")
    print("各縣市匯入數量：")

    for city, count in city_counts.items():
        print(f"{city}：{count} 筆")


if __name__ == "__main__":
    scrape_attractions()