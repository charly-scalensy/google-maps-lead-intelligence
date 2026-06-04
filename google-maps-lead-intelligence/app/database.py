import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "places.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            industry TEXT,
            address TEXT,
            rating REAL,
            review_count INTEGER,
            phone TEXT,
            website TEXT,
            price_range TEXT,
            maps_url TEXT,
            recent_reviews TEXT,
            negative_keywords TEXT,
            priority_score INTEGER,
            priority_label TEXT,
            recommended_angle TEXT,
            scrape_date TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_places(places: list):
    conn = sqlite3.connect(DB_PATH)
    for p in places:
        conn.execute("""
            INSERT INTO places (
                name, industry, address, rating, review_count, phone, website,
                price_range, maps_url, recent_reviews, negative_keywords,
                priority_score, priority_label, recommended_angle, scrape_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p.get("name"), p.get("industry"), p.get("address"),
            p.get("rating"), p.get("review_count"), p.get("phone"),
            p.get("website"), p.get("price_range"), p.get("maps_url"),
            json.dumps(p.get("recent_reviews", [])),
            json.dumps(p.get("negative_keywords", [])),
            p.get("priority_score"), p.get("priority_label"),
            p.get("recommended_angle"),
            p.get("scrape_date", datetime.now().strftime("%Y-%m-%d %H:%M"))
        ))
    conn.commit()
    conn.close()


def get_places() -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM places ORDER BY priority_score DESC, id DESC"
    ).fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["recent_reviews"] = json.loads(d.get("recent_reviews") or "[]")
        d["negative_keywords"] = json.loads(d.get("negative_keywords") or "[]")
        result.append(d)
    return result


def clear_places():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM places")
    conn.commit()
    conn.close()
