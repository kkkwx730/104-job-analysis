import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_attractions(keyword=None):
    conn = get_connection()
    cur = conn.cursor()

    if keyword:
        search_text = f"%{keyword}%"
        cur.execute("""
            SELECT name, city, category, website
            FROM attractions
            WHERE name ILIKE %s
               OR city ILIKE %s
               OR category ILIKE %s
            ORDER BY id;
        """, (search_text, search_text, search_text))
    else:
        cur.execute("""
            SELECT name, city, category, website
            FROM attractions
            ORDER BY id;
        """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_city_analysis():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT city, COUNT(*) AS total
        FROM attractions
        GROUP BY city
        ORDER BY total DESC;
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_category_analysis():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT category, COUNT(*) AS total
        FROM attractions
        GROUP BY category
        ORDER BY total DESC;
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/attractions")
def attractions():
    keyword = request.args.get("keyword", "")
    data = get_attractions(keyword)
    return render_template(
        "attractions.html",
        attractions=data,
        keyword=keyword
    )


@app.route("/analysis")
def analysis():
    city_data = get_city_analysis()
    category_data = get_category_analysis()

    return render_template(
        "analysis.html",
        city_data=city_data,
        category_data=category_data
    )


if __name__ == "__main__":
    app.run(debug=True)