# -*- coding: utf-8 -*-
from typing import List, Optional
from datetime import datetime
from config.database import get_db
from models.notification import Notification

def _row_to_notif(r) -> Notification:
    return Notification(
        id=r[0], client_id=r[1], type_notification=r[2],
        canal=r[3], message=r[4], statut=r[5],
        date_creation=r[6], date_envoi=r[7]
    )

def get_all() -> List[Notification]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, client_id, type_notification, canal, message, statut, date_creation, date_envoi FROM notifications ORDER BY date_creation DESC")
        rows = cur.fetchall()
    return [_row_to_notif(r) for r in rows]

def create(n: Notification) -> Notification:
    with get_db() as (cur, conn):
        cur.execute(
            "INSERT INTO notifications (client_id, type_notification, canal, message, statut, date_envoi) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, date_creation",
            (n.client_id, n.type_notification, n.canal, n.message, n.statut, n.date_envoi)
        )
        row = cur.fetchone()
        n.id = row[0]
        n.date_creation = row[1]
    return n

def mark_as_sent(notif_id: int) -> None:
    with get_db() as (cur, conn):
        cur.execute("UPDATE notifications SET statut='envoye', date_envoi=CURRENT_TIMESTAMP WHERE id=%s", (notif_id,))
