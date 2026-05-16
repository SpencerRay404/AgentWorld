from __future__ import annotations

import csv
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TxType(str, Enum):
    EARNING = "EARNING"
    PAYMENT = "PAYMENT"
    PENALTY = "PENALTY"
    ADJUSTMENT = "ADJUSTMENT"


class Ledger:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def record(
        self,
        agent_id: str,
        amount: float,
        tx_type: TxType,
        tick: int,
        cycle: int,
        notes: str = "",
    ) -> None:
        self._conn.execute(
            """INSERT INTO transactions (agent_id, amount, tx_type, tick, cycle, timestamp, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (agent_id, amount, tx_type.value, tick, cycle, _utcnow().isoformat(), notes),
        )
        self._conn.commit()

    def get_balance(self, agent_id: str) -> float:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0.0) FROM transactions WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        return float(row[0])

    def get_cycle_earnings(self, agent_id: str, cycle: int) -> float:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(amount), 0.0) FROM transactions WHERE agent_id = ? AND cycle = ?",
            (agent_id, cycle),
        ).fetchone()
        return float(row[0])

    def get_population_totals(self, cycle: Optional[int] = None) -> Dict[str, float]:
        if cycle is None:
            rows = self._conn.execute(
                "SELECT agent_id, COALESCE(SUM(amount), 0.0) FROM transactions GROUP BY agent_id"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT agent_id, COALESCE(SUM(amount), 0.0) FROM transactions WHERE cycle = ? GROUP BY agent_id",
                (cycle,),
            ).fetchall()
        return {r[0]: float(r[1]) for r in rows}

    def export_csv(self, path: str) -> None:
        rows = self._conn.execute(
            "SELECT tx_id, agent_id, amount, tx_type, tick, cycle, timestamp, notes FROM transactions ORDER BY tx_id"
        ).fetchall()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tx_id", "agent_id", "amount", "tx_type", "tick", "cycle", "timestamp", "notes"])
            writer.writerows(rows)
