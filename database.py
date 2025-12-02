from sqlalchemy import create_engine, text
import os

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

engine = create_engine("sqlite:///data/data.db", future=True)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bundles(
                id TEXT PRIMARY KEY,
                json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """))

def save_bundle(bundle_id: str, json_str: str, created_at: str):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT OR REPLACE INTO bundles (id, json, created_at) VALUES (:i, :j, :c)"),
            {"i": bundle_id, "j": json_str, "c": created_at}
        )
