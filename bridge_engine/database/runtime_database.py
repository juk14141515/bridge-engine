import sqlite3
from pathlib import Path


DB_PATH = Path("data/runtime.db")


class RuntimeDatabase:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(DB_PATH)
        self.initialize_tables()

    def initialize_tables(self):
        cursor = self.connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS runtime_lanes (
                lane_id TEXT PRIMARY KEY,
                status TEXT,
                current_goal TEXT,
                interest_frame TEXT,
                cognitive_mode TEXT,
                next_action TEXT,
                progress REAL,
                runtime_json TEXT
            )
            '''
        )

        self.connection.commit()
