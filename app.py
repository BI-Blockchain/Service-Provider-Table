# import streamlit as st
# from datetime import date

# from database.database import init_db
# from database.locations import get_locations, add_location
# from database.providers import get_providers, add_provider
# from services.schedule_service import save_schedule
# from services.csv_service import generate_csv_bytes

# st.set_page_config(page_title="Provider Schedule Management", page_icon="📅", layout="wide")
# init_db()

# st.title("📅 Provider Schedule Management System")
# st.caption("Each location can have multiple providers. Set hours for each selected provider and generate the output CSV.")

# with st.sidebar:
#     st.header("Management")
#     with st.expander("➕ Add New Location", expanded=False):
#         new_location = st.text_input("Location name", key="new_location")
#         if st.button("Save Location", use_container_width=True):
#             name = new_location.strip()
#             if not name:
#                 st.error("Enter a location name.")
#             elif add_location(name):
#                 st.success(f"Location '{name}' added.")
#                 st.rerun()
#             else:
#                 st.warning("That location already exists.")

#     with st.expander("➕ Add New Provider", expanded=False):
#         new_provider = st.text_input("Provider name", key="new_provider")
#         if st.button("Save Provider", use_container_width=True):
#             name = new_provider.strip()
#             if not name:
#                 st.error("Enter a provider name.")
#             elif add_provider(name):
#                 st.success(f"Provider '{name}' added.")
#                 st.rerun()
#             else:
#                 st.warning("That provider already exists.")

# selected_date = st.date_input("Select Date", value=date.today())
# locations = get_locations()
# providers = get_providers()

# if not locations:
#     st.warning("No locations exist yet. Add locations from the sidebar.")
#     st.stop()
# if not providers:
#     st.warning("No providers exist yet. Add providers from the sidebar.")
#     st.stop()

# provider_names = [p["name"] for p in providers]

# st.subheader(f"Location / Provider Selection — {selected_date.strftime('%A, %d %B %Y')}")
# st.info("Use the multi-select box to choose more than one provider for the same location.")

# h1, h2, h3 = st.columns([2.0, 3.0, 1.8])
# h1.markdown("**Location**")
# h2.markdown("**Providers — select multiple**")
# h3.markdown("**Working Hours**")

# all_rows = []

# for loc in locations:
#     loc_id = loc["id"]
#     location_name = loc["name"]
#     c1, c2, c3 = st.columns([2.0, 3.0, 1.8])
#     c1.write(location_name)

#     provider_key = f"providers_{loc_id}_{selected_date.isoformat()}"
#     selected_providers = c2.multiselect(
#         f"Providers for {location_name}",
#         provider_names,
#         key=provider_key,
#         placeholder="Select one or more providers",
#         label_visibility="collapsed",
#     )

#     if selected_providers:
#         with c3:
#             st.caption("Hours per selected provider")
#             for provider_name in selected_providers:
#                 hour_key = f"hours_{selected_date.isoformat()}_{loc_id}_{provider_name}"
#                 if hour_key not in st.session_state:
#                     st.session_state[hour_key] = 8.0
#                 hours = st.number_input(
#                     provider_name,
#                     min_value=0.0,
#                     max_value=8.0,
#                     value=float(st.session_state[hour_key]),
#                     step=0.5,
#                     key=hour_key,
#                 )
#                 all_rows.append({
#                     "location_id": loc_id,
#                     "location": location_name,
#                     "provider": provider_name,
#                     "working_hours": float(hours),
#                 })
#     else:
#         c3.caption("Default: 8 hours")

# st.divider()
# st.subheader("Selected Schedule")

# if all_rows:
#     preview = [{
#         "Date": selected_date.strftime("%Y-%m-%d"),
#         "Location": r["location"],
#         "Provider": r["provider"],
#         "Working Hours": r["working_hours"],
#     } for r in all_rows]
#     st.dataframe(preview, use_container_width=True, hide_index=True)
#     st.write(f"**Selected schedule rows:** {len(all_rows)}")

#     c1, c2 = st.columns(2)
#     with c1:
#         if st.button("💾 Save Schedule", type="primary", use_container_width=True):
#             saved = save_schedule(selected_date, all_rows)
#             st.success(f"Saved {saved} schedule row(s).")
#     with c2:
#         csv_bytes = generate_csv_bytes(selected_date, all_rows)
#         st.download_button(
#             "⬇️ Download Output CSV",
#             data=csv_bytes,
#             file_name=f"schedule_{selected_date.isoformat()}.csv",
#             mime="text/csv",
#             use_container_width=True,
#         )
# else:
#     st.info("Select at least one provider from a location to create the CSV.")

# st.divider()
# st.caption("Default working hours: 8. Maximum working hours: 8. A location can have multiple providers.")


# import streamlit as st
# from datetime import date

# from database.database import init_db

# from database.locations import (
#     get_locations,
#     add_location,
#     delete_location
# )

# from database.providers import (
#     get_providers,
#     add_provider,
#     delete_provider
# )

# from services.schedule_service import save_schedule
# from services.csv_service import generate_csv_bytes


# # ============================================================
# # PAGE CONFIGURATION
# # ============================================================

# st.set_page_config(
#     page_title="Provider Schedule Management",
#     page_icon="📅",
#     layout="wide"
# )


# # ============================================================
# # INITIALIZE DATABASE
# # ============================================================

# init_db()


# # ============================================================
# # PROVIDER NAME PARSER
# # ============================================================

# def parse_provider_name(provider_name):
#     """
#     Convert provider values like:

#         Cze-Ja(Tam,Cze-Ja,NP)

#     into:

#         Appointment Servicing Provider = Cze-Ja
#         Title = NP

#     Another example:

#         Benjamin

#     becomes:

#         Appointment Servicing Provider = Benjamin
#         Title = ""

#     Another example:

#         Cze-Ja(Tam,Cze-Ja)

#     becomes:

#         Appointment Servicing Provider = Cze-Ja
#         Title = Cze-Ja
#     """

#     provider_name = str(provider_name).strip()

#     # --------------------------------------------------------
#     # No parentheses
#     # --------------------------------------------------------

#     if "(" not in provider_name:

#         return provider_name, ""


#     # --------------------------------------------------------
#     # Find parentheses
#     # --------------------------------------------------------

#     start = provider_name.find("(")
#     end = provider_name.rfind(")")


#     # Invalid parentheses
#     if start == -1 or end == -1 or end <= start:

#         return provider_name, ""


#     # --------------------------------------------------------
#     # Provider name = everything before "("
#     # --------------------------------------------------------

#     servicing_provider = provider_name[
#         :start
#     ].strip()


#     # --------------------------------------------------------
#     # Content inside parentheses
#     # --------------------------------------------------------

#     inside = provider_name[
#         start + 1:end
#     ].strip()


#     # --------------------------------------------------------
#     # Title = LAST value inside parentheses
#     #
#     # Example:
#     #
#     # Tam,Cze-Ja,NP
#     #
#     # Title = NP
#     # --------------------------------------------------------

#     title = ""

#     if inside:

#         parts = [
#             part.strip()
#             for part in inside.split(",")
#             if part.strip()
#         ]

#         if parts:

#             title = parts[-1]


#     return servicing_provider, title


# # ============================================================
# # PAGE TITLE
# # ============================================================

# st.title(
#     "📅 Provider Schedule Management System"
# )

# st.caption(
#     "Select providers for each location, set working hours, "
#     "save the schedule, and generate the final CSV."
# )


# # ============================================================
# # SIDEBAR
# # ============================================================

# with st.sidebar:

#     st.header("Management")


#     # ========================================================
#     # ADD LOCATION
#     # ========================================================

#     with st.expander(
#         "➕ Add New Location",
#         expanded=False
#     ):

#         new_location = st.text_input(
#             "Location name",
#             key="new_location"
#         )


#         if st.button(
#             "Save Location",
#             use_container_width=True
#         ):

#             name = new_location.strip()


#             if not name:

#                 st.error(
#                     "Enter a location name."
#                 )

#             elif add_location(name):

#                 st.success(
#                     f"Location '{name}' added."
#                 )

#                 st.rerun()

#             else:

#                 st.warning(
#                     "That location already exists."
#                 )


#     # ========================================================
#     # DELETE LOCATION
#     # ========================================================

#     with st.expander(
#         "🗑️ Delete Location",
#         expanded=False
#     ):

#         locations_for_delete = get_locations()


#         if locations_for_delete:

#             location_options = {
#                 loc["name"]: loc["id"]
#                 for loc in locations_for_delete
#             }


#             delete_location_name = st.selectbox(
#                 "Select location to delete",
#                 list(location_options.keys()),
#                 key="delete_location_select"
#             )


#             st.warning(
#                 "Deleting a location cannot be undone."
#             )


#             if st.button(
#                 "🗑️ Delete Location",
#                 use_container_width=True
#             ):

#                 location_id = location_options[
#                     delete_location_name
#                 ]


#                 deleted = delete_location(
#                     location_id
#                 )


#                 if deleted:

#                     st.success(
#                         f"Location '{delete_location_name}' deleted."
#                     )

#                     st.rerun()

#                 else:

#                     st.error(
#                         "Could not delete the location."
#                     )

#         else:

#             st.info(
#                 "No locations available."
#             )


#     # ========================================================
#     # ADD PROVIDER
#     # ========================================================

#     with st.expander(
#         "➕ Add New Provider",
#         expanded=False
#     ):

#         new_provider = st.text_input(
#             "Provider name",
#             key="new_provider"
#         )


#         if st.button(
#             "Save Provider",
#             use_container_width=True
#         ):

#             name = new_provider.strip()


#             if not name:

#                 st.error(
#                     "Enter a provider name."
#                 )

#             elif add_provider(name):

#                 st.success(
#                     f"Provider '{name}' added."
#                 )

#                 st.rerun()

#             else:

#                 st.warning(
#                     "That provider already exists."
#                 )


#     # ========================================================
#     # DELETE PROVIDER
#     # ========================================================

#     with st.expander(
#         "🗑️ Delete Provider",
#         expanded=False
#     ):

#         providers_for_delete = get_providers()


#         if providers_for_delete:

#             provider_options = {
#                 provider["name"]: provider["id"]
#                 for provider in providers_for_delete
#             }


#             delete_provider_name = st.selectbox(
#                 "Select provider to delete",
#                 list(provider_options.keys()),
#                 key="delete_provider_select"
#             )


#             st.warning(
#                 "Deleting a provider cannot be undone."
#             )


#             if st.button(
#                 "🗑️ Delete Provider",
#                 use_container_width=True
#             ):

#                 provider_id = provider_options[
#                     delete_provider_name
#                 ]


#                 deleted = delete_provider(
#                     provider_id
#                 )


#                 if deleted:

#                     st.success(
#                         f"Provider '{delete_provider_name}' deleted."
#                     )

#                     st.rerun()

#                 else:

#                     st.error(
#                         "Could not delete the provider."
#                     )


# # ============================================================
# # DATE
# # ============================================================

# selected_date = st.date_input(
#     "Select Date",
#     value=date.today()
# )


# # ============================================================
# # LOAD LOCATIONS AND PROVIDERS
# # ============================================================

# locations = get_locations()

# providers = get_providers()


# if not locations:

#     st.warning(
#         "No locations exist yet. "
#         "Add locations from the sidebar."
#     )

#     st.stop()


# if not providers:

#     st.warning(
#         "No providers exist yet. "
#         "Add providers from the sidebar."
#     )

#     st.stop()


# # ============================================================
# # PROVIDER NAMES
# # ============================================================

# provider_names = [
#     provider["name"]
#     for provider in providers
# ]


# # ============================================================
# # LOCATION / PROVIDER SELECTION
# # ============================================================

# st.subheader(
#     f"Location / Provider Selection — "
#     f"{selected_date.strftime('%A, %d %B %Y')}"
# )


# st.info(
#     "Select one or more providers for each location."
# )


# h1, h2, h3 = st.columns(
#     [2.0, 3.0, 1.8]
# )


# h1.markdown("**Location**")

# h2.markdown("**Providers — select multiple**")

# h3.markdown("**Working Hours**")


# # ============================================================
# # STORE SELECTED ROWS
# # ============================================================

# all_rows = []


# # ============================================================
# # LOCATIONS
# # ============================================================

# for loc in locations:

#     loc_id = loc["id"]

#     location_name = loc["name"]


#     c1, c2, c3 = st.columns(
#         [2.0, 3.0, 1.8]
#     )


#     # --------------------------------------------------------
#     # LOCATION
#     # --------------------------------------------------------

#     c1.write(location_name)


#     # --------------------------------------------------------
#     # PROVIDER MULTISELECT
#     # --------------------------------------------------------

#     provider_key = (
#         f"providers_"
#         f"{loc_id}_"
#         f"{selected_date.isoformat()}"
#     )


#     selected_providers = c2.multiselect(

#         f"Providers for {location_name}",

#         provider_names,

#         key=provider_key,

#         placeholder="Select one or more providers",

#         label_visibility="collapsed"

#     )


#     # ========================================================
#     # SELECTED PROVIDERS
#     # ========================================================

#     if selected_providers:

#         with c3:

#             st.caption(
#                 "Hours per selected provider"
#             )


#             for provider_name in selected_providers:


#                 # ------------------------------------------------
#                 # HOURS KEY
#                 # ------------------------------------------------

#                 hour_key = (
#                     f"hours_"
#                     f"{selected_date.isoformat()}_"
#                     f"{loc_id}_"
#                     f"{provider_name}"
#                 )


#                 if hour_key not in st.session_state:

#                     st.session_state[
#                         hour_key
#                     ] = 8.0


#                 # ------------------------------------------------
#                 # HOURS INPUT
#                 # ------------------------------------------------

#                 hours = st.number_input(

#                     provider_name,

#                     min_value=0.0,

#                     max_value=8.0,

#                     value=float(
#                         st.session_state[
#                             hour_key
#                         ]
#                     ),

#                     step=0.5,

#                     key=hour_key

#                 )


#                 # =================================================
#                 # PARSE PROVIDER
#                 # =================================================

#                 servicing_provider, title = (
#                     parse_provider_name(
#                         provider_name
#                     )
#                 )


#                 # =================================================
#                 # STORE ROW
#                 # =================================================

#                 all_rows.append({

#                     "location_id": loc_id,

#                     "location": location_name,

#                     # Original provider
#                     "provider": provider_name,

#                     # Parsed provider
#                     "servicing_provider":
#                         servicing_provider,

#                     # Parsed title
#                     "title": title,

#                     "working_hours":
#                         float(hours)

#                 })


#     else:

#         c3.caption(
#             "Default: 8 hours"
#         )


# # ============================================================
# # FINAL SCHEDULE
# # ============================================================

# st.divider()

# st.subheader(
#     "Selected Schedule"
# )


# if all_rows:

#     # ========================================================
#     # CREATE FINAL OUTPUT TABLE
#     # ========================================================

#     preview = [

#         {
#             "Appointment Date":
#                 selected_date.strftime(
#                     "%Y-%m-%d"
#                 ),

#             "Appointment Servicing Provider":
#                 row["servicing_provider"],

#             "WH":
#                 row["working_hours"],

#             "Title":
#                 row["title"],

#             "Main Location":
#                 row["location"]

#         }

#         for row in all_rows

#     ]


#     # ========================================================
#     # DISPLAY FINAL TABLE
#     # ========================================================

#     st.dataframe(

#         preview,

#         use_container_width=True,

#         hide_index=True

#     )


#     st.write(
#         f"**Selected schedule rows:** "
#         f"{len(all_rows)}"
#     )


#     # ========================================================
#     # SAVE / DOWNLOAD
#     # ========================================================

#     c1, c2 = st.columns(2)


#     # ========================================================
#     # SAVE SCHEDULE
#     # ========================================================

#     with c1:

#         if st.button(
#             "💾 Save Schedule",
#             type="primary",
#             use_container_width=True
#         ):

#             saved = save_schedule(
#                 selected_date,
#                 all_rows
#             )


#             st.success(
#                 f"Saved {saved} schedule row(s)."
#             )


#     # ========================================================
#     # DOWNLOAD CSV
#     # ========================================================

#     with c2:

#         # ----------------------------------------------------
#         # Prepare final CSV rows
#         # ----------------------------------------------------

#         csv_rows = [

#             {
#                 "appointment_date":
#                     selected_date.strftime(
#                         "%Y-%m-%d"
#                     ),

#                 "appointment_servicing_provider":
#                     row["servicing_provider"],

#                 "wh":
#                     row["working_hours"],

#                 "title":
#                     row["title"],

#                 "main_location":
#                     row["location"]

#             }

#             for row in all_rows

#         ]


#         # ----------------------------------------------------
#         # Generate CSV
#         # ----------------------------------------------------

#         csv_bytes = generate_csv_bytes(
#             selected_date,
#             csv_rows
#         )


#         # ----------------------------------------------------
#         # Download
#         # ----------------------------------------------------

#         st.download_button(

#             "⬇️ Download Output CSV",

#             data=csv_bytes,

#             file_name=(
#                 f"schedule_"
#                 f"{selected_date.isoformat()}.csv"
#             ),

#             mime="text/csv",

#             use_container_width=True

#         )


# else:

#     st.info(
#         "Select at least one provider from a location "
#         "to create the CSV."
#     )


# # ============================================================
# # FOOTER
# # ============================================================

# st.divider()

# st.caption(
#     "Default working hours: 8. "
#     "Maximum working hours: 8. "
#     "A location can have multiple providers."
# )






# new
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
#   di(Actual Name,Title)  ->  ("Actual Name", "Title")
#   Cze-Ja(Tam,Cze-Ja,NP)  ->  ("Cze-Ja", "NP")
#   Ben(NP)                ->  ("Ben", "NP")
#   Benjamin               ->  ("Benjamin", "")
#
# Title              = LAST value inside the parentheses
# Servicing provider = SECOND-TO-LAST value inside the parentheses
#                      (if only one value, the text before "(")
# ============================================================

def parse_provider_name(provider_name):

    provider_name = str(provider_name).strip()

    if "(" not in provider_name:
        return provider_name, ""

    start = provider_name.find("(")
    end = provider_name.rfind(")")

    if end == -1 or end <= start:
        return provider_name, ""

    before = provider_name[:start].strip()

    inside = provider_name[start + 1:end].strip()

    parts = [p.strip() for p in inside.split(",") if p.strip()]

    if not parts:
        return before, ""

    title = parts[-1]

    if len(parts) >= 2:
        servicing_provider = parts[-2]
    else:
        servicing_provider = before

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