from database.database import get_connection

def get_providers():
    conn=get_connection(); rows=conn.execute("SELECT id,name FROM providers WHERE active=1 ORDER BY name").fetchall(); conn.close(); return [dict(r) for r in rows]

def add_provider(name):
    conn=get_connection()
    try:
        conn.execute("INSERT INTO providers(name) VALUES(?)",(name,)); conn.commit(); return True
    except Exception: return False
    finally: conn.close()
