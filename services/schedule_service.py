from database.schedules import save_schedule_row
from database.providers import get_providers
from config import DEFAULT_WORKING_HOURS, MAX_WORKING_HOURS

def save_schedule(schedule_date, rows):
    provider_map = {p["name"]: p["id"] for p in get_providers()}
    saved = 0
    for row in rows:
        provider_id = provider_map.get(row.get("provider"))
        if provider_id is None:
            continue
        hours = row.get("working_hours", DEFAULT_WORKING_HOURS)
        hours = min(max(float(hours), 0), MAX_WORKING_HOURS)
        save_schedule_row(schedule_date.isoformat(), row["location_id"], provider_id, hours)
        saved += 1
    return saved
