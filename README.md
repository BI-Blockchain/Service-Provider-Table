# Provider Schedule Management Application

## Updated feature: multiple providers per location

Each location now has a **multi-select provider box**. More than one provider can be selected for the same location.

Example:

```text
Van Nuys
[ Bhatt, Shelat, CZE-JA ]

Bhatt   [8]
Shelat  [4]
CZE-JA  [8]
```

The output CSV contains one row for each location/provider combination.

## Features

- No input CSV is required
- Select a date
- Start with 25 locations by adding them to the database
- Add more locations later
- Add more providers later
- Select multiple providers for the same location
- Set working hours separately for each selected provider
- Default working hours = 8
- Maximum working hours = 8
- Save schedules to SQLite
- Download output CSV

## Run on Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The database is automatically created at `data/schedule.db`.

## Output example

```csv
Date,Location,Provider,Working Hours
2026-09-30,Van Nuys,Bhatt,8
2026-09-30,Van Nuys,Shelat,4
2026-09-30,San Fernando,Alex,8
```
