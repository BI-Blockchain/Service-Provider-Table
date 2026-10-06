import re
from config import DEFAULT_WORKING_HOURS, MAX_WORKING_HOURS
TIME_PATTERN=re.compile(r'(?<!\d)(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?\s*[-–]\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM)?(?!\d)',re.I)

def calculate_working_hours(time_text):
    if not time_text: return DEFAULT_WORKING_HOURS
    m=TIME_PATTERN.search(str(time_text))
    if not m: return DEFAULT_WORKING_HOURS
    sh,sm,sa=int(m.group(1)),int(m.group(2) or 0),(m.group(3) or '').upper(); eh,em,ea=int(m.group(4)),int(m.group(5) or 0),(m.group(6) or '').upper()
    if ea and not sa: sa=ea
    def mins(h,m,a):
        if a=='AM' and h==12: h=0
        elif a=='PM' and h!=12: h+=12
        return h*60+m
    start=mins(sh,sm,sa); end=mins(eh,em,ea)
    if not sa and not ea: start=sh*60+sm; end=eh*60+em
    if end<start: end+=720
    return min(max((end-start)/60,0),MAX_WORKING_HOURS)
