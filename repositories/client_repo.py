from config.database import get_connection
from models.client import Client

def get_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, prenom, telephone, email, adresse, date_creation FROM clients ORDER BY nom")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [Client(id=r[0], nom=r[1], prenom=r[2], telephone=r[3], email=r[4], adresse=r[5], date_creation=r[6]) for r in rows]

def get_by_id(client_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom, prenom, telephone, email, adresse, date_creation FROM clients WHERE id=%s", (client_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    if r:
        return Client(id=r[0], nom=r[1], prenom=r[2], telephone=r[3], email=r[4], adresse=r[5], date_creation=r[6])
    return None

def search(query: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nom, prenom, telephone, email, adresse FROM clients WHERE nom ILIKE %s OR prenom ILIKE %s OR telephone ILIKE %s ORDER BY nom",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    )
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [Client(id=r[0], nom=r[1], prenom=r[2], telephone=r[3], email=r[4], adresse=r[5]) for r in rows]

def create(client: Client):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clients (nom, prenom, telephone, email, adresse) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (client.nom, client.prenom, client.telephone, client.email, client.adresse)
    )
    client.id = cur.fetchone()[0]
    conn.commit(); cur.close(); conn.close()
    return client

def update(client: Client):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE clients SET nom=%s, prenom=%s, telephone=%s, email=%s, adresse=%s WHERE id=%s",
        (client.nom, client.prenom, client.telephone, client.email, client.adresse, client.id)
    )
    conn.commit(); cur.close(); conn.close()

def delete(client_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Supprimer dans l'ordre pour respecter les FK
        cur.execute("""
            DELETE FROM factures WHERE client_id = %s;
            DELETE FROM ordres_reparation WHERE vehicule_id IN 
                (SELECT id FROM vehicules WHERE client_id = %s);
            DELETE FROM vehicules WHERE client_id = %s;
            DELETE FROM clients WHERE id = %s;
        """, (client_id, client_id, client_id, client_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()