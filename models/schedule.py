from dataclasses import dataclass
@dataclass
class Schedule:
    schedule_date:str
    location_id:int
    provider_id:int
    working_hours:float
