import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


conn = get_connection()

df = pd.read_sql("SELECT city, category FROM attractions;", conn)

conn.close()

# ===== 各縣市景點數 =====
city = df["city"].value_counts()

plt.figure(figsize=(10,5))
city.plot(kind="bar")
plt.title("Number of Attractions by City")
plt.xlabel("City")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("static/city_chart.png")
plt.close()

# ===== 景點類型 =====
category = df["category"].value_counts()

plt.figure(figsize=(8,8))
category.plot(kind="pie", autopct="%1.1f%%")
plt.ylabel("")
plt.title("Attraction Category")
plt.tight_layout()
plt.savefig("static/category_chart.png")
plt.close()

print("分析圖完成")