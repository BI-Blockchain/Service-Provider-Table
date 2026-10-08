import csv
import io
import sqlite3
from datetime import date

import streamlit as st

import database.database as _db_module
from database.database import init_db

from database.locations import get_locations, add_location
from database.providers import get_providers, add_provider

from services.schedule_service import save_schedule


# ============================================================
# DELETE FUNCTIONS
# Uses delete_location / delete_provider from the database
# modules when they exist, otherwise falls back to these.
# ============================================================

def _open_connection():
    for fn_name in ("get_connection", "get_conn", "get_db", "connect"):
        fn = getattr(_db_module, fn_name, None)
        if callable(fn):
            return fn()

    for attr in ("DB_PATH", "DB_NAME", "DATABASE", "DATABASE_PATH", "DB_FILE"):
        path = getattr(_db_module, attr, None)
        if path:
            return sqlite3.connect(str(path))

    raise RuntimeError(
        "Could not find the database connection in database/database.py"
    )


def _delete_row(table, row_id):
    conn = _open_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


try:
    from database.locations import delete_location
except ImportError:
    def delete_location(location_id):
        return _delete_row("locations", location_id)


try:
    from database.providers import delete_provider
except ImportError:
    def delete_provider(provider_id):
        return _delete_row("providers", provider_id)


# ============================================================
# CSV BUILDER (self-contained, no csv_service needed)
# ============================================================

CSV_HEADERS = [
    "Appointment Date",
    "Appointment Servicing Provider",
    "WH",
    "Title",
    "Main Location",
]


def build_csv_bytes(selected_date, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")

    writer.writerow(CSV_HEADERS)

    for row in rows:
        writer.writerow([
            selected_date.strftime("%Y-%m-%d"),
            row["servicing_provider"],
            row["working_hours"],
            row["title"],
            row["location"],
        ])

    return buffer.getvalue().encode("utf-8")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Provider Schedule Management",
    page_icon="📅",
    layout="wide",
)

init_db()


# ============================================================
# PROVIDER NAME PARSER
#
#   Jose((Vargas, Jose) ,PA)  ->  ("Vargas, Jose", "PA")
#   di(Actual Name,Title)     ->  ("Actual Name", "Title")
#   Cze-Ja(Tam,Cze-Ja,NP)     ->  ("Cze-Ja", "NP")
#   Ben(NP)                   ->  ("Ben", "NP")
#   Benjamin                  ->  ("Benjamin", "")
#
# Rules (applied to the text inside the OUTER parentheses,
# split on commas that are NOT inside inner parentheses):
#
#   Title              = LAST value
#   Servicing provider = SECOND-TO-LAST value, with any
#                        wrapping parentheses removed
#                        (if there is only one value,
#                        the text before the outer "(")
# ============================================================

def _split_top_level(text):
    """Split on commas that are not inside parentheses."""

    parts = []
    current = []
    depth = 0

    for ch in text:

        if ch == "(":
            depth += 1
            current.append(ch)

        elif ch == ")":
            depth = max(depth - 1, 0)
            current.append(ch)

        elif ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []

        else:
            current.append(ch)

    parts.append("".join(current).strip())

    return [p for p in parts if p]


def _strip_wrapping_parens(text):
    """'(Vargas, Jose)' -> 'Vargas, Jose'"""

    text = text.strip()

    while text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()

    return text


def parse_provider_name(provider_name):

    provider_name = str(provider_name).strip()

    # No parentheses
    if "(" not in provider_name:
        return provider_name, ""

    start = provider_name.find("(")
    end = provider_name.rfind(")")

    # Invalid parentheses
    if end == -1 or end <= start:
        return provider_name, ""

    before = provider_name[:start].strip()

    inside = provider_name[start + 1:end].strip()

    parts = _split_top_level(inside)

    if not parts:
        return before, ""

    # Only one value inside the outer parentheses
    if len(parts) == 1:

        only = parts[0]

        # Jose((Vargas, Jose))  -> provider only, no title
        if only.startswith("("):
            return _strip_wrapping_parens(only), ""

        # Ben(NP) -> provider = Ben, title = NP
        return before, only

    title = parts[-1]

    servicing_provider = _strip_wrapping_parens(parts[-2])

    return servicing_provider, title


# ============================================================
# PAGE TITLE
# ============================================================

st.title("📅 Provider Schedule Management System")

st.caption(
    "Select providers for each location, set working hours, "
    "save the schedule, and generate the final CSV."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Management")

    # ---------------- ADD LOCATION ----------------

    with st.expander("➕ Add New Location", expanded=False):

        new_location = st.text_input("Location name", key="new_location")

        if st.button("Save Location", use_container_width=True):

            name = new_location.strip()

            if not name:
                st.error("Enter a location name.")
            elif add_location(name):
                st.success(f"Location '{name}' added.")
                st.rerun()
            else:
                st.warning("That location already exists.")

    # ---------------- DELETE LOCATION ----------------

    with st.expander("🗑️ Delete Location", expanded=False):

        locations_for_delete = get_locations()

        if locations_for_delete:

            location_options = {
                loc["name"]: loc["id"] for loc in locations_for_delete
            }

            delete_location_name = st.selectbox(
                "Select location to delete",
                list(location_options.keys()),
                key="delete_location_select",
            )

            st.warning("Deleting a location cannot be undone.")

            if st.button(
                "🗑️ Delete Location",
                use_container_width=True,
                key="delete_location_button",
            ):
                if delete_location(location_options[delete_location_name]):
                    st.success(f"Location '{delete_location_name}' deleted.")
                    st.rerun()
                else:
                    st.error("Could not delete the location.")

        else:
            st.info("No locations available.")

    # ---------------- ADD PROVIDER ----------------

    with st.expander("➕ Add New Provider", expanded=False):

        new_provider = st.text_input("Provider name", key="new_provider")

        if st.button("Save Provider", use_container_width=True):

            name = new_provider.strip()

            if not name:
                st.error("Enter a provider name.")
            elif add_provider(name):
                st.success(f"Provider '{name}' added.")
                st.rerun()
            else:
                st.warning("That provider already exists.")

    # ---------------- DELETE PROVIDER ----------------

    with st.expander("🗑️ Delete Provider", expanded=False):

        providers_for_delete = get_providers()

        if providers_for_delete:

            provider_options = {
                p["name"]: p["id"] for p in providers_for_delete
            }

            delete_provider_name = st.selectbox(
                "Select provider to delete",
                list(provider_options.keys()),
                key="delete_provider_select",
            )

            st.warning("Deleting a provider cannot be undone.")

            if st.button(
                "🗑️ Delete Provider",
                use_container_width=True,
                key="delete_provider_button",
            ):
                if delete_provider(provider_options[delete_provider_name]):
                    st.success(f"Provider '{delete_provider_name}' deleted.")
                    st.rerun()
                else:
                    st.error("Could not delete the provider.")

        else:
            st.info("No providers available.")


# ============================================================
# DATE
# ============================================================

selected_date = st.date_input("Select Date", value=date.today())


# ============================================================
# LOAD LOCATIONS AND PROVIDERS
# ============================================================

locations = get_locations()
providers = get_providers()

if not locations:
    st.warning("No locations exist yet. Add locations from the sidebar.")
    st.stop()

if not providers:
    st.warning("No providers exist yet. Add providers from the sidebar.")
    st.stop()

provider_names = [p["name"] for p in providers]


# ============================================================
# LOCATION / PROVIDER SELECTION
# ============================================================

st.subheader(
    f"Location / Provider Selection — "
    f"{selected_date.strftime('%A, %d %B %Y')}"
)

st.info("Select one or more providers for each location.")

h1, h2, h3 = st.columns([2.0, 3.0, 1.8])

h1.markdown("**Location**")
h2.markdown("**Providers — select multiple**")
h3.markdown("**Working Hours**")

all_rows = []

for loc in locations:

    loc_id = loc["id"]
    location_name = loc["name"]

    c1, c2, c3 = st.columns([2.0, 3.0, 1.8])

    c1.write(location_name)

    provider_key = f"providers_{loc_id}_{selected_date.isoformat()}"

    selected_providers = c2.multiselect(
        f"Providers for {location_name}",
        provider_names,
        key=provider_key,
        placeholder="Select one or more providers",
        label_visibility="collapsed",
    )

    if selected_providers:

        with c3:

            st.caption("Hours per selected provider")

            for provider_name in selected_providers:

                hour_key = (
                    f"hours_{selected_date.isoformat()}_"
                    f"{loc_id}_{provider_name}"
                )

                if hour_key not in st.session_state:
                    st.session_state[hour_key] = 8.0

                hours = st.number_input(
                    provider_name,
                    min_value=0.0,
                    max_value=8.0,
                    step=0.5,
                    key=hour_key,
                )

                servicing_provider, title = parse_provider_name(provider_name)

                all_rows.append({
                    "location_id": loc_id,
                    "location": location_name,
                    "provider": provider_name,
                    "servicing_provider": servicing_provider,
                    "title": title,
                    "working_hours": float(hours),
                })

    else:
        c3.caption("Default: 8 hours")


# ============================================================
# FINAL SCHEDULE
# ============================================================

st.divider()

st.subheader("Selected Schedule")

if all_rows:

    preview = [
        {
            "Appointment Date": selected_date.strftime("%Y-%m-%d"),
            "Appointment Servicing Provider": row["servicing_provider"],
            "WH": row["working_hours"],
            "Title": row["title"],
            "Main Location": row["location"],
        }
        for row in all_rows
    ]

    st.dataframe(preview, use_container_width=True, hide_index=True)

    st.write(f"**Selected schedule rows:** {len(all_rows)}")

    c1, c2 = st.columns(2)

    # ---------------- SAVE SCHEDULE ----------------

    with c1:

        if st.button(
            "💾 Save Schedule",
            type="primary",
            use_container_width=True,
        ):
            saved = save_schedule(selected_date, all_rows)
            st.success(f"Saved {saved} schedule row(s).")

    # ---------------- DOWNLOAD CSV ----------------

    with c2:

        st.download_button(
            "⬇️ Download Output CSV",
            data=build_csv_bytes(selected_date, all_rows),
            file_name=f"schedule_{selected_date.isoformat()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

else:

    st.info(
        "Select at least one provider from a location to create the CSV."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Default working hours: 8. "
    "Maximum working hours: 8. "
    "A location can have multiple providers."
)