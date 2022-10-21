# main.py
##################################################################################################################
# IMPORT PACKAGES
import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import gspread
import pandas as pd
from st_aggrid import AgGrid
st.set_page_config(page_title='Privilege Assigner App by LPM', page_icon='https://raw.githubusercontent.com/pyinstaller/pyinstaller/develop/PyInstaller/bootloader/images/icon-windowed.ico', layout="wide")
##################################################################################################################
# LOGIN INFO
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("Password incorrect")
        return False
    else:
        # Password correct.
        return True
##################################################################################################################
if check_password():
    # IMPORTANT FUNCTIONS
    
    # @st.experimental_memo
    def get_connection_object():
        """
        Create a connection object. 

        Note: @st.experimental_singleton is a key-value store that's shared across 
        all sessions of a Streamlit app. It's great for storing heavyweight singleton 
        objects across sessions, like database connections.
        """
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                    "https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file", 
                    "https://www.googleapis.com/auth/drive"
                    ],
        )
        client = gspread.authorize(credentials)
        return client

    # @st.experimental_memo
    def get_sheet(name_of_file):
        """
        Read database from connection object, get whole spreadsheet
        """
        client = get_connection_object()
        return client.open(name_of_file)

    @st.experimental_memo
    def get_worksheet(supervisor_name, sheet):
        """
        Get privileges for given supervisor name. This function
        gets a worksheet within spreadsheet named after supervisor.
        """
        worksheet = sheet.worksheet(supervisor_name)
        return worksheet

    @st.experimental_memo
    def get_stored_data(shit_supervisors):
        # Store all current privileges
        holder = dict()
        for count, item in enumerate(shit_supervisors):
            # holder[item] = pd.DataFrame(sheet.worksheet(item).col_values(1)[1:])
            _ = pd.DataFrame(sheet.worksheet(item).col_values(1))
            holder[item] = _
        return holder

    shit_supervisors = []
    shit_departments = st.secrets['departments']
    ##################################################################################################################
    # DATA AND WIDGETS
    # Title
    st.header('Privilege assigning program by LPM')

    # Get data
    sheet = get_sheet("private-spreadsheet")

    # Add already existing supervisors to list
    worksheet_list = sheet.worksheets()
    # st.experimental_show(worksheet_list)

    # This add a supervisor not in the original list, so you don't have to edit by hand all the time
    for i in worksheet_list:
        inner = str(i.title)
        if inner not in shit_supervisors:
            shit_supervisors.append(inner)
            # st.experimental_show(shit_supervisors)

    # Create a worksheet for each of the sups if one doesn't exist
    for count, item in enumerate(shit_supervisors):
        try:
            # Add worksheet with sup name
            sheet.add_worksheet(title=shit_supervisors[count], rows=20, cols=1)
        except:
            pass
        # st.write(item)

        #########################################################
        # UNCOMMENT TO DELETE ALL WORKSHEETS
        # sheet.del_worksheet(sheet.worksheet(item))
        #########################################################

    ##################################################################################################################
    # ADD NEW SUPERVISOR
    with st.expander("Click here to add a new supervisor"):
        new_sup = st.text_input('Name')
        if st.button('Add'):
            sheet.add_worksheet(title=new_sup, rows=20, cols=1)
            shit_supervisors.append(new_sup)
            st.success("New supervisor added successfully")

    st.subheader("Choose supervisor to look at:")
    sup =  st.selectbox('Choose supervisor', options=shit_supervisors)

    ##################################################################################################################
    # REMOVE SUPERVISOR
    with st.expander("Click here to remove a supervisor"):
        _worksheet = sheet.worksheet(sup)
        if st.button('Delete supervisor'):
            sheet.del_worksheet(_worksheet)
            st.success(f"Successfully deleted {sup}")
            get_stored_data.clear()
            st.experimental_rerun()

    ##################################################################################################################
    # ADD PRIVILEGES
    with st.expander('Click here to add a new department to this supervisor'):
        dept = st.selectbox('Choose department to be added', options=shit_departments)
        if st.button('Add department'):
            _worksheet = sheet.worksheet(sup)
            if dept in list(_worksheet.col_values(1)):
                pass
                st.warning("Deparment has already been assigned")
            else:
                _worksheet.insert_row([dept], 1)
                st.success(f"Deparment {dept} has been assigned to {sup}")
            get_stored_data.clear()

    ##################################################################################################################
    # REMOVE PRIVILES
    with st.expander("Click here to remove a department from this supervisor"):
        _worksheet = sheet.worksheet(sup)
        dept_to_remove = st.selectbox('Choose department to remove:', options=_worksheet.col_values(1))
        if st.button('Delete department'):
            cell = _worksheet.find(dept_to_remove)
            _worksheet.delete_row(cell.row)
            st.success(f"Department {dept_to_remove} removed from {sup}'s privileges")
            get_stored_data.clear()

    ##################################################################################################################
    # SHOW CURRENT PRIVILEGES IN TWO COLUMNS
    # Show data
    st.subheader("Currently assigned privileges:")
    holder = get_stored_data(shit_supervisors)
    col1, col2 = st.columns(2)
    for count, i in enumerate(holder.keys()):
        if count %2 == 0:
            with col1: 
                st.write(i)
                st.dataframe(holder.get(i), use_container_width=True)
        else:
            with col2:
                st.write(i)
                st.dataframe(holder.get(i), use_container_width=True)



# import streamlit as st
# from google.oauth2 import service_account
# from gsheetsdb import connect

# # Create a connection object.
# credentials = service_account.Credentials.from_service_account_info(
#     st.secrets["gcp_service_account"],
#     scopes=[
#         "https://www.googleapis.com/auth/spreadsheets",
#     ],
# )
# conn = connect(credentials=credentials)

# # Perform SQL query on the Google Sheet.
# # Uses st.cache to only rerun when the query changes or after 10 min.
# @st.cache(ttl=600)
# def run_query(query):
#     rows = conn.execute(query, headers=1)
#     rows = rows.fetchall()
#     return rows

# sheet_url = st.secrets["private_gsheets_url"]
# rows = run_query(f'SELECT * FROM "{sheet_url}"')

# # Print results.
# for row in rows:
# #     st.write(f"{row.supervisor} has access to :{row.department}:")
#     st.write(row)
