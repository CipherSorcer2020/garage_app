# -*- coding: utf-8 -*-
from typing import List, Optional
from config.database import get_db
from models.audit_log import AuditLog

def _row_to_log(r) -> AuditLog:
    return AuditLog(
        id=r[0], user_id=r[1], action=r[2], entity=r[3],
        entity_id=r[4], timestamp=r[5], details=r[6]
    )

def create(log: AuditLog) -> AuditLog:
    with get_db() as (cur, conn):
        cur.execute(
            """INSERT INTO audit_logs (user_id, action, entity, entity_id, timestamp, details)
               VALUES (%s,%s,%s,%s,COALESCE(%s, CURRENT_TIMESTAMP),%s)
               RETURNING id, timestamp""",
            (log.user_id, log.action, log.entity, log.entity_id, log.timestamp, log.details)
        )
        row = cur.fetchone()
        log.id = row[0]
        log.timestamp = row[1]
    return log

def list_all() -> List[AuditLog]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, user_id, action, entity, entity_id, timestamp, details FROM audit_logs ORDER BY timestamp DESC")
        rows = cur.fetchall()
    return [_row_to_log(r) for r in rows]

def filter_by_user(user_id: int) -> List[AuditLog]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, user_id, action, entity, entity_id, timestamp, details FROM audit_logs WHERE user_id=%s ORDER BY timestamp DESC", (user_id,))
        rows = cur.fetchall()
    return [_row_to_log(r) for r in rows]
