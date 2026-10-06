import csv, io

def generate_csv_bytes(schedule_date, rows):
    out=io.StringIO(); w=csv.writer(out)
    w.writerow(['Date','Location','Provider','Working Hours'])
    for r in rows: w.writerow([schedule_date.strftime('%Y-%m-%d'),r['location'],r['provider'],r['working_hours']])
    return out.getvalue().encode('utf-8-sig')
