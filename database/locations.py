from database.database import get_connection

def get_locations():
    conn=get_connection(); rows=conn.execute("SELECT id,name FROM locations WHERE active=1 ORDER BY id").fetchall(); conn.close(); return [dict(r) for r in rows]

def add_location(name):
    conn=get_connection()
    try:
        conn.execute("INSERT INTO locations(name) VALUES(?)",(name,)); conn.commit(); return True
    except Exception: return False
    finally: conn.close()
