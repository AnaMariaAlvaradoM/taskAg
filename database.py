import sqlite3

DB = "tasks.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                done    INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

def add_task(name: str) -> int:
    with sqlite3.connect(DB) as conn:
        cur = conn.execute("INSERT INTO tasks (name) VALUES (?)", (name,))
        return cur.lastrowid

def get_tasks(done=False):
    with sqlite3.connect(DB) as conn:
        if done is None:
            return conn.execute("SELECT id, name, done FROM tasks ORDER BY id").fetchall()
        return conn.execute(
            "SELECT id, name, done FROM tasks WHERE done = ? ORDER BY id",
            (1 if done else 0,)
        ).fetchall()

def complete_task(task_id: int):
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT name FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row:
            conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
            return row[0]
        return None

def get_progress():
    with sqlite3.connect(DB) as conn:
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done  = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
        pct   = round((done / total * 100) if total > 0 else 0)
        return total, done, pct