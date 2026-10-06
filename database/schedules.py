from database.database import get_connection

def save_schedule_row(schedule_date, location_id, provider_id, working_hours):
    conn = get_connection()
    conn.execute('''
        INSERT INTO schedules (schedule_date, location_id, provider_id, working_hours)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(schedule_date, location_id, provider_id)
        DO UPDATE SET working_hours = excluded.working_hours
    ''', (schedule_date, location_id, provider_id, working_hours))
    conn.commit()
    conn.close()
