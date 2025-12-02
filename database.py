from sqlalchemy import create_engine, text
from loguru import logger
from exceptions import DatabaseError

engine = create_engine("sqlite:///data.db", future=True)

def init_db():
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bundles(
                    id TEXT PRIMARY KEY,
                    json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """))
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise DatabaseError(
            "Fehler bei der Datenbankinitialisierung",
            details={"error": str(e)}
        )

def save_bundle(bundle_id: str, json_str: str, created_at: str):
    try:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT OR REPLACE INTO bundles (id, json, created_at) VALUES (:i, :j, :c)"),
                {"i": bundle_id, "j": json_str, "c": created_at}
            )
        logger.info(f"Bundle saved to database: {bundle_id}")
    except Exception as e:
        logger.error(f"Failed to save bundle to database: {str(e)}")
        raise DatabaseError(
            "Fehler beim Speichern des Bundles in der Datenbank",
            details={"bundle_id": bundle_id, "error": str(e)}
        )
