# main.py

import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

# Print results.
for row in rows:
#     st.write(f"{row.supervisor} has access to :{row.department}:")
    st.write(row)

    
# crud - alternative way of doing this: https://shritam.medium.com/google-sheets-a-database-c4e3fef6e0bc
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from pprint import pprint

# # scope of the application
# scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
#          "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# credentials = ServiceAccountCredentials.from_json_keyfile_name(
#     "/home/shritam/Google_sheet_project/Cred.json", scope)

# client = gspread.authorize(credentials)


# # Open the spreadhseet
# sheet = client.open("Zalando Data").worksheet("zalando_data")

# # Get a list of all records
# data = sheet.get_all_records()
# pprint(data)
