# -*- coding: utf-8 -*-
# Repository Data Access Layer for diagnostic_repo
# Executes raw SQL queries and maps result rows to data models.

from config.database import get_connection
from models.diagnostic import Diagnostic

def get_by_or(or_id: int):
    """
    Handles database operations for function 'get_by_or'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, or_id, observations, date_diagnostic FROM diagnostics WHERE or_id=%s", (or_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return Diagnostic(id=r[0], or_id=r[1], observations=r[2], date_diagnostic=r[3]) if r else None

def create(d: Diagnostic):
    """
    Handles database operations for function 'create'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO diagnostics (or_id, observations, date_diagnostic) VALUES (%s,%s,CURRENT_DATE) RETURNING id",
        (d.or_id, d.observations)
    )
    d.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return d

def update(d: Diagnostic):
    """
    Handles database operations for function 'update'.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE diagnostics SET observations=%s WHERE id=%s", (d.observations, d.id))
    conn.commit(); cur.close(); conn.close()