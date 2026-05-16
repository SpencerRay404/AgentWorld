import sqlite3


CREATE_AGENTS = """
CREATE TABLE IF NOT EXISTS agents (
    agent_id    TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    role_type   TEXT NOT NULL,
    risk_tolerance  REAL NOT NULL,
    rest_preference REAL NOT NULL,
    efficiency      REAL NOT NULL,
    created_at  TEXT NOT NULL
)
"""

CREATE_AGENT_STATES = """
CREATE TABLE IF NOT EXISTS agent_states (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id        TEXT NOT NULL,
    status          TEXT NOT NULL,
    energy          REAL NOT NULL,
    balance         REAL NOT NULL,
    current_tick    INTEGER NOT NULL,
    last_action     TEXT NOT NULL,
    consecutive_work_ticks INTEGER NOT NULL,
    recorded_at     TEXT NOT NULL
)
"""

CREATE_LIFECYCLE_EVENTS = """
CREATE TABLE IF NOT EXISTS lifecycle_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    tick        INTEGER NOT NULL,
    timestamp   TEXT NOT NULL,
    notes       TEXT DEFAULT ''
)
"""


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(CREATE_AGENTS)
    cur.execute(CREATE_AGENT_STATES)
    cur.execute(CREATE_LIFECYCLE_EVENTS)
    conn.commit()
    return conn
