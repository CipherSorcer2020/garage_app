# -*- coding: utf-8 -*-
from typing import List, Optional
from config.database import get_db
from models.or_photo import ORPhoto

def _row_to_photo(r) -> ORPhoto:
    return ORPhoto(
        id=r[0],
        or_id=r[1],
        description=r[2],
        image_data=r[3],
        date_ajout=r[4]
    )

def get_by_or(or_id: int) -> List[ORPhoto]:
    with get_db() as (cur, conn):
        cur.execute("SELECT id, or_id, description, image_data, date_ajout FROM or_photos WHERE or_id=%s ORDER BY date_ajout ASC", (or_id,))
        rows = cur.fetchall()
    return [_row_to_photo(r) for r in rows]

def create(photo: ORPhoto) -> ORPhoto:
    with get_db() as (cur, conn):
        cur.execute(
            "INSERT INTO or_photos (or_id, description, image_data, date_ajout) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING id, date_ajout",
            (photo.or_id, photo.description, photo.image_data)
        )
        row = cur.fetchone()
        photo.id = row[0]
        photo.date_ajout = row[1]
    return photo

def delete(photo_id: int) -> None:
    with get_db() as (cur, conn):
        cur.execute("DELETE FROM or_photos WHERE id=%s", (photo_id,))
