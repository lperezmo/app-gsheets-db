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
    # HELPER FUNCTIONS
    @st.experimental_memo
    def get_assigned_access():
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                    "https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file", 
                    "https://www.googleapis.com/auth/drive"
                    ],
        )
        # conn = connect(credentials=credentials)
        client = gspread.authorize(credentials)

        # # @st.experimental_memo(ttl=600)
        # def run_pseudo_query():
        #     sheet = client.open('private-spreadsheet')
        #     return sheet

        sheet = client.open('private-spreadsheet')
        current_supervisors = []
        _current_supervisors = sheet.worksheets()
        for i in _current_supervisors:
            current_supervisors.append(str(i.title))

        holder = dict()
        for n in current_supervisors:
            _ = pd.DataFrame(sheet.worksheet(n).col_values(1))
            holder[n] = _

        # Clear memory for reloading data
        access_to_by_supervisor.clear()
        get_assigned_access.clear()

        return current_supervisors, holder

    @st.experimental_memo
    def create_supervisor(new_sup):
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                    "https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file", 
                    "https://www.googleapis.com/auth/drive"
                    ],
        )
        # conn = connect(credentials=credentials)
        client = gspread.authorize(credentials)

        # Get sheet
        sheet = client.open('private-spreadsheet')

        # Add supervisor
        sheet.add_worksheet(title=new_sup, rows=20, cols=1)

        # Clear memory for reloading data
        access_to_by_supervisor.clear()
        get_assigned_access.clear()

    @st.experimental_memo
    def delete_supervisor(sup_name):
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                    "https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file", 
                    "https://www.googleapis.com/auth/drive"
                    ],
        )

        # Get sheet
        client = gspread.authorize(credentials)
        sheet = client.open('private-spreadsheet')

        # Delete supervisor
        worksheet = sheet.worksheet(sup_name)
        sheet.del_worksheet(worksheet)
        st.success(f"Successfully deleted {sup_name}")

        # Clear memory for reloading data
        access_to_by_supervisor.clear()
        get_assigned_access.clear()

    @st.experimental_memo
    def add_deparment_to_supervisor(sup_name, department_to_add):
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                    "https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file", 
                    "https://www.googleapis.com/auth/drive"
                    ],
        )
        # Get sheet
        client = gspread.authorize(credentials)
        sheet = client.open('private-spreadsheet')
        worksheet = sheet.worksheet(sup_name)

        # Add deparment
        if department_to_add in list(worksheet.col_values(1)):
            st.warning("Deparment has already been assigned")
        else:
            worksheet.insert_row([department_to_add], 1)
            st.success(f"Deparment {department_to_add} has been assigned to {sup_name}")

        # Clear memory for reloading data
        access_to_by_supervisor.clear()
        get_assigned_access.clear()

    @st.experimental_memo
    def remove_department_from_supervisor(sup_name, dept_to_remove):
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                    "https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file", 
                    "https://www.googleapis.com/auth/drive"
                    ],
        )
        # Get sheet
        client = gspread.authorize(credentials)
        sheet = client.open('private-spreadsheet')
        worksheet = sheet.worksheet(sup_name)

        # Delete department to remove
        cell = worksheet.find(dept_to_remove)
        worksheet.delete_row(cell.row)
        st.success(f"Department {dept_to_remove} removed from {sup}'s privileges")

        # Clear memory for reloading data
        access_to_by_supervisor.clear()
        get_assigned_access.clear()

    @st.experimental_memo
    def access_to_by_supervisor(sup_name):
        # Create a connection object.
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                    "https://spreadsheets.google.com/feeds", 
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file", 
                    "https://www.googleapis.com/auth/drive"
                    ],
        )
        # conn = connect(credentials=credentials)
        client = gspread.authorize(credentials)

        # Get worksheet
        sheet = client.open('private-spreadsheet')
        worksheet = sheet.worksheet(sup_name)
        list_of_access = worksheet.col_values(1)

        return list_of_access

    ##################################################################################################################
    # MAIN PROGRAM

    # Title
    st.header('Privilege assigning program by LPM')
    
    # Get list of departments from secrets
    departments = sorted(st.secrets['departments'])
    
    st.subheader("Current privileges")
    with st.expander("Click here"):
        # Get current assigned access to show
        current_supervisors, holder = get_assigned_access()
        current_supervisors = sorted(current_supervisors)
        for i in holder.keys():
            try:
                tablita = list(holder.get(i).iloc[0])
                st.markdown(f"* {i} has access to {tablita}")
            except:
                pass

    # Manage current supervisors (select one at a time)
    st.subheader('Manage existing supervisors:')
    with st.expander("Click here"):
        # Select supervisor and get its list of access
        sup =  st.selectbox('Choose supervisor to manage', options=current_supervisors)
        try:
            list_of_access = sorted(list(holder.get(sup).iloc[0]))
        except:
            list_of_access = []
        
        # Option for adding department
        dept_to_add = st.selectbox('Add a new department to this supervisor', options=departments)
        if st.button('Add department'):
            add_deparment_to_supervisor(dept_to_add)

        # Remove privileges
        dept_to_remove = st.selectbox('Remove a department from this supervisor', options=list_of_access)
        if st.button('Delete department'):
            remove_department_from_supervisor(dept_to_remove)

        # Option for removing supervisor
        if st.button('Delete this supervisor'):
                delete_supervisor(sup)

    # New supervisors
    st.subheader("Add a new supervisor")
    with st.expander("Click here"):
        new_sup = st.text_input('Input name of new supervisor')
        if st.button('Add new supervisor'):
            create_supervisor(new_sup)
