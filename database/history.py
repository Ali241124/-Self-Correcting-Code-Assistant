
import sqlite3
import json

from pathlib import Path
from datetime import datetime, timezone


# ---------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------

DATABASE_PATH = Path(__file__).parent / "history.db"


# ---------------------------------------
# DATABASE CONNECTION
# ---------------------------------------

def get_connection(db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------

def initialize_database(db_path=DATABASE_PATH):

    with get_connection(db_path) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS debugging_history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                original_code TEXT NOT NULL,

                final_code TEXT,

                test_code TEXT,

                success INTEGER NOT NULL,

                message TEXT,

                attempts INTEGER DEFAULT 0,

                execution_output TEXT,

                validation_json TEXT,

                history_json TEXT,

                created_at TEXT NOT NULL

            )
        """)

        connection.commit()


# ---------------------------------------
# SAVE DEBUGGING SESSION
# ---------------------------------------

def save_run(
    original_code,
    result,
    test_code=None,
    db_path=DATABASE_PATH
):

    execution_result = result.get("execution_result") or {}

    validation = result.get("validation") or {}

    history = result.get("history", [])

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection(db_path) as connection:

        cursor = connection.execute("""

            INSERT INTO debugging_history (

                original_code,
                final_code,
                test_code,
                success,
                message,
                attempts,
                execution_output,
                validation_json,
                history_json,
                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            original_code,
            result.get("final_code", ""),
            test_code,
            int(result.get("success", False)),
            result.get("message", ""),
            result.get("attempts", 0),
            execution_result.get("stdout", ""),
            json.dumps(validation),
            json.dumps(history),
            created_at

        ))

        connection.commit()

        return cursor.lastrowid


# ---------------------------------------
# GET RECENT HISTORY
# ---------------------------------------

def get_recent_runs(limit=20, db_path=DATABASE_PATH):

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be a positive integer.")

    with get_connection(db_path) as connection:

        rows = connection.execute("""

            SELECT *
            FROM debugging_history
            ORDER BY id DESC
            LIMIT ?

        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


# ---------------------------------------
# GET ONE DEBUGGING SESSION
# ---------------------------------------

def get_run_by_id(run_id, db_path=DATABASE_PATH):

    with get_connection(db_path) as connection:

        row = connection.execute("""

            SELECT *
            FROM debugging_history
            WHERE id = ?

        """, (run_id,)).fetchone()

        return dict(row) if row else None


# ---------------------------------------
# DELETE DEBUGGING SESSION
# ---------------------------------------

def delete_run(run_id, db_path=DATABASE_PATH):

    with get_connection(db_path) as connection:

        cursor = connection.execute("""

            DELETE FROM debugging_history
            WHERE id = ?

        """, (run_id,))

        connection.commit()

        return cursor.rowcount > 0
