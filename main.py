import streamlit as st
import pyodbc
import pandas as pd

# Page configuration
st.set_page_config(page_title='Remote SQL demonstration', 
		   page_icon='https://raw.githubusercontent.com/pyinstaller/pyinstaller/develop/PyInstaller/bootloader/images/icon-windowed.ico', 
		   layout="wide")

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
	"""
	Perform query using experimental memo to rerun only when the query changes
	or after 10 min.
	"""
	with conn.cursor() as cur:
		cur.execute(query)
		cur.fetchall()
		df = pd.read_sql(query, conn)
		print(f"Query executed successfully at {pd.Timestamp('now').__str__()}")
		return df

# Run query and display results.
query = """SELECT TOP (1000) [EmployeeID]
	,[LastName]
	,[FirstName]
	,[Title]
	,[TitleOfCourtesy]
	,[BirthDate]
	,[HireDate]
	,[Address]
	,[City]
	,[Region]
	,[PostalCode]
	,[Country]
	,[HomePhone]
	,[Extension]
	,[Photo]
	,[Notes]
	,[ReportsTo]
	,[PhotoPath]
	FROM [Northwind].[dbo].[Employees]"""
query = query.replace('\n', ' ')
df= run_query(query)

st.success(f"Successfully connected to remote Azure SQL database and retrieved the data displayed below on {pd.Timestamp('now').__str__()}")
st.dataframe(df)
st.write("Note: This app whitelists only the six stable outbound IP addresses used by the app's cloud services to allow selective access to this SQL database")
st.write("Disclaimer: All data used on this app is fictional and was obtained from Northwind and pubs sample databases for Microsoft SQL Server available at "
	 "https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/northwind-pubs")
###################################################################################
###################################################################################
# Here is original application, testing remote SQL server above
# ##################################################################################################################
# # IMPORT PACKAGES
# import streamlit as st
# from google.oauth2 import service_account
# # from gsheetsdb import connect
# import gspread
# import pandas as pd
# # from st_aggrid import AgGrid
# import networkx as nx 
# from pyvis.network import Network
# import streamlit.components.v1 as components
# st.set_page_config(page_title='Privilege Assigner App by LPM', page_icon='https://raw.githubusercontent.com/pyinstaller/pyinstaller/develop/PyInstaller/bootloader/images/icon-windowed.ico', layout="wide")
# ##################################################################################################################
# # LOGIN INFO
# def check_password():
#     """Returns `True` if the user had the correct password."""

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if st.session_state["password"] == st.secrets["password"]:
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]  # don't store password
#         else:
#             st.session_state["password_correct"] = False

#     if "password_correct" not in st.session_state:
#         # First run, show input for password.
#         st.text_input(
#             "Password", type="password", on_change=password_entered, key="password"
#         )
#         return False
#     elif not st.session_state["password_correct"]:
#         # Password not correct, show input + error.
#         st.text_input(
#             "Password", type="password", on_change=password_entered, key="password"
#         )
#         st.error("Password incorrect")
#         return False
#     else:
#         # Password correct.
#         return True
# ##################################################################################################################
# if check_password():
#     # HELPER FUNCTIONS
#     @st.experimental_singleton
#     def get_assigned_access():
#         # Create a connection object.
#         credentials = service_account.Credentials.from_service_account_info(
#             st.secrets["gcp_service_account"],
#             scopes=[
#                     "https://spreadsheets.google.com/feeds", 
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive.file", 
#                     "https://www.googleapis.com/auth/drive"
#                     ],
#         )
#         # conn = connect(credentials=credentials)
#         client = gspread.authorize(credentials)

#         # # @st.experimental_memo(ttl=600)
#         # def run_pseudo_query():
#         #     sheet = client.open('private-spreadsheet')
#         #     return sheet

#         sheet = client.open('private-spreadsheet')
#         current_supervisors = []
#         _current_supervisors = sheet.worksheets()
#         for i in _current_supervisors:
#             if str(i.title) == 'Unassigned':
#                 unassigned = sheet.worksheet('Unassigned').col_values(1)
#             else:
#                 current_supervisors.append(str(i.title))

#         holder = dict()
#         for n in current_supervisors:
#             _ = pd.DataFrame(sheet.worksheet(n).col_values(1))
#             _.dropna()
#             holder[n] = _

#         return current_supervisors, holder, unassigned

#     @st.experimental_memo
#     def create_supervisor(new_sup):
#         # Create a connection object.
#         credentials = service_account.Credentials.from_service_account_info(
#             st.secrets["gcp_service_account"],
#             scopes=[
#                     "https://spreadsheets.google.com/feeds", 
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive.file", 
#                     "https://www.googleapis.com/auth/drive"
#                     ],
#         )
#         # conn = connect(credentials=credentials)
#         client = gspread.authorize(credentials)

#         # Get sheet
#         sheet = client.open('private-spreadsheet')

#         # Add supervisor
#         sheet.add_worksheet(title=new_sup, rows=20, cols=1)

#         # Clear memory for reloading data
#         # access_to_by_supervisor.clear()
#         # get_assigned_access.clear()

#     @st.experimental_memo
#     def delete_supervisor(sup_name):
#         # Create a connection object.
#         credentials = service_account.Credentials.from_service_account_info(
#             st.secrets["gcp_service_account"],
#             scopes=[
#                     "https://spreadsheets.google.com/feeds", 
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive.file", 
#                     "https://www.googleapis.com/auth/drive"
#                     ],
#         )

#         # Get sheet
#         client = gspread.authorize(credentials)
#         sheet = client.open('private-spreadsheet')

#         # Delete supervisor
#         worksheet = sheet.worksheet(sup_name)
#         sheet.del_worksheet(worksheet)
#         st.success(f"Successfully deleted {sup_name}")

#         # Clear memory for reloading data
#         # access_to_by_supervisor.clear()
#         # get_assigned_access.clear()

#     @st.experimental_memo
#     def add_deparment_to_supervisor(sup_name, department_to_add):
#         # Create a connection object.
#         credentials = service_account.Credentials.from_service_account_info(
#             st.secrets["gcp_service_account"],
#             scopes=[
#                     "https://spreadsheets.google.com/feeds", 
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive.file", 
#                     "https://www.googleapis.com/auth/drive"
#                     ],
#         )
#         # Get sheet
#         client = gspread.authorize(credentials)
#         sheet = client.open('private-spreadsheet')
#         worksheet = sheet.worksheet(sup_name)

#         # Add deparment
#         if department_to_add in list(worksheet.col_values(1)[0:49]):
#             st.warning("Deparment has already been assigned")
#         else:
#             worksheet.insert_row([department_to_add], 1)
#             st.success(f"Deparment {department_to_add} has been assigned to {sup_name}")

#         # Clear memory for reloading data
#         # access_to_by_supervisor.clear()
#         # get_assigned_access.clear()

#     @st.experimental_memo
#     def remove_department_from_supervisor(sup_name, dept_to_remove):
#         # Create a connection object.
#         credentials = service_account.Credentials.from_service_account_info(
#             st.secrets["gcp_service_account"],
#             scopes=[
#                     "https://spreadsheets.google.com/feeds", 
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive.file", 
#                     "https://www.googleapis.com/auth/drive"
#                     ],
#         )
#         # Get sheet
#         client = gspread.authorize(credentials)
#         sheet = client.open('private-spreadsheet')
#         worksheet = sheet.worksheet(sup_name)

#         # Delete department to remove
#         cell = worksheet.find(dept_to_remove)
#         worksheet.delete_row(cell.row)
#         st.success(f"Department {dept_to_remove} removed from {sup}'s privileges")

        
#     @st.experimental_memo
#     def add_unassigned(sup_name, person_to_add):
#         # Create a connection object.
#         credentials = service_account.Credentials.from_service_account_info(
#             st.secrets["gcp_service_account"],
#             scopes=[
#                     "https://spreadsheets.google.com/feeds", 
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive.file", 
#                     "https://www.googleapis.com/auth/drive"
#                     ],
#         )
#         # Get sheet
#         client = gspread.authorize(credentials)
#         sheet = client.open('private-spreadsheet')
#         worksheet = sheet.worksheet(sup_name)

#         # Add person to add
#         # NOTE: EVERYTHING PAST ROW 50 IS UNASSIGNED PEOPLE
#         if person_to_add in list(worksheet.col_values(1)[50:]):
#             st.warning("Deparment has already been assigned")
#         else:
#             worksheet.insert_row([person_to_add], 50)
#             st.success(f"Deparment {person_to_add} has been assigned to {sup_name}")
        
    
#     @st.experimental_memo
#     def remove_unassigned(sup_name, person_to_remove):
#         # Create a connection object.
#         credentials = service_account.Credentials.from_service_account_info(
#             st.secrets["gcp_service_account"],
#             scopes=[
#                     "https://spreadsheets.google.com/feeds", 
#                     "https://www.googleapis.com/auth/spreadsheets",
#                     "https://www.googleapis.com/auth/drive.file", 
#                     "https://www.googleapis.com/auth/drive"
#                     ],
#         )
#         # Get sheet
#         client = gspread.authorize(credentials)
#         sheet = client.open('private-spreadsheet')
#         worksheet = sheet.worksheet(sup_name)

#         # Delete department to remove
#         cell = worksheet.find(person_to_remove)
#         worksheet.delete_row(cell.row)
#         st.success(f"Department {person_to_remove} removed from {sup}'s privileges")
        
#     ##################################################################################################################
#     # MAIN PROGRAM

#     # Title
#     st.header('Privilege Assigner App')
#     st.caption("Written & designed by Luis Perez Morales")
    
#     # Get list of departments from secrets
#     departments = sorted(st.secrets['departments'])
    
#     # Get current assigned access to show
#     current_supervisors, holder, unassigned = get_assigned_access()
#     current_supervisors = sorted(current_supervisors)
    
#     st.subheader(":scroll: Current privileges")
#     with st.expander("Click here"):
#         selection = st.selectbox('Select a supervisor:', options = sorted(holder.keys()))
#         if selection:
#             try:
#                 # Assigned departments
#                 st.write('Assigned departments:')
#                 tablita = list(holder.get(selection)[0][:40])
#                 tablita = list(filter(None, tablita))
#                 st.table(tablita)
#                 # Filter empty stuff on departments


#                 # Assigned people
#                 st.write("Assigned people:")
#                 tablita_people = list(holder.get(selection)[0][40:])
#                 tablita_people = list(filter(None, tablita_people))
#                 st.table(tablita_people)
#             except:
#                 st.warning('No departments or people assigned to this supervisor.')
            
#             # Option to list all access at once
#             if st.button('Just list all data at once in a list'):
#                 for i in holder.keys():
#                     try:
#                         tablita = list(filter(None, list(holder.get(i)[0][:40])))
#                         tablita_people = list(filter(None, list(holder.get(i)[0][40:])))
#                         st.markdown(f"* {i} has access to following departments {tablita} \n and the following people \n {tablita_people}")
#                     except:
#                         pass
#             # Optional button to reload app & re-run app
#             if st.button("Refresh all data & reload app"):
#                 get_assigned_access.clear()
#                 st.experimental_rerun()
#                 st.success("App and data reloaded")
#                 st.snow()

#     # Manage current supervisors (select one at a time)
#     st.subheader(':pencil2: Manage existing supervisors:')
#     with st.expander("Click here"):
#         # Select supervisor and get its list of access
#         sup =  st.selectbox('Choose supervisor to manage', options=current_supervisors)
#         try:
#             # Improved list of access based on "tablita" above
#             list_of_access = list(holder.get(sup)[0][:49])
#             list_of_access = sorted(list(filter(None, list_of_access)))
#         except:
#             list_of_access = []
            
#         try:
#             # List of unassigned
#             # Based on "tablita_people" above
#             # Important to remove 'None' because when inserting new departments
#             # the values of employees will move down the spreadsheet
#             list_of_una = sorted(list(holder.get(sup)[0][49:]))
#             list_of_una = list(filter(None, list_of_una))
#         except:
#             list_of_una = []
        
#         # Option for adding department
#         st.markdown("### 1. Add a new department to this supervisor")
#         dept_to_add = st.selectbox('Add a new department to this supervisor', options=departments, label_visibility="collapsed")
#         if st.button('Add department'):
#             add_deparment_to_supervisor(sup, dept_to_add)

#         # Remove privileges
#         st.markdown("### 2. Remove a department from this supervisor")
#         dept_to_remove = st.selectbox('Remove a department from this supervisor', options=list_of_access, label_visibility="collapsed")
#         if st.button('Delete department'):
#             remove_department_from_supervisor(sup, dept_to_remove)

#         # Add unassigned person
#         st.markdown("### 3. Add a new unassigned employee to this supervisor")
#         person_to_add = st.selectbox('Add a new unassigned employee to this supervisor', options=unassigned, label_visibility="collapsed")
#         if st.button('Add unassigned employee'):
#             add_unassigned(sup, person_to_add)
            
#          # Remove unassigned person
#         st.markdown("### 4. Remove an unassigned employee from this supervisor")
#         person_to_remove = st.selectbox('Remove an unassigned employee from this supervisor', options=list_of_una, label_visibility="collapsed")
#         if st.button('Delete unassigned employee'):
#             remove_unassigned(sup, person_to_remove)
            
#         # Option for removing supervisor
#         if st.button('Delete this supervisor'):
#             delete_supervisor(sup)
                

#     # New supervisors
#     st.subheader(":new: Add a new supervisor")
#     with st.expander("Click here"):
#         new_sup = st.text_input('Input name of new supervisor')
#         if st.button('Add new supervisor'):
#             create_supervisor(new_sup)

###################################################################################
###################################################################################
            
# For reading privileges:
# @st.experimental_singleton
# def get_assigned_access():
#     # Create a connection object.
#     credentials = service_account.Credentials.from_service_account_info(
#         st.secrets["gcp_service_account"],
#         scopes=[
#                 "https://spreadsheets.google.com/feeds", 
#                 "https://www.googleapis.com/auth/spreadsheets",
#                 "https://www.googleapis.com/auth/drive.file", 
#                 "https://www.googleapis.com/auth/drive"
#                 ],
#     )

#     # Get sheet
#     client = gspread.authorize(credentials)
#     sheet = client.open('private-spreadsheet')

#     # Get current supervisors & their access to depts and people
#     _current_supervisors = sheet.worksheets()
#     current_supervisors = []
#     dept_access = dict()
#     people_access = dict()

#     for i in _current_supervisors:
#         sup = str(i.title)
#         if sup == 'Unassigned':
#             # Get all unassigned
#             unassigned = sheet.worksheet('Unassigned').col_values(1)
#         else:
#             # Get supervisors & access
#             current_supervisors.append(sup)
#             col_values = pd.DataFrame(sheet.worksheet(sup).col_values(1))
#             try:
#                 # Assigned departments
#                 tablita = list(col_values[0][:40])
#                 tablita = list(filter(None, tablita))
#                 dept_access[sup] = tablita
#             except:
#                 dept_access[sup] = []
#             try:
#                 # Assigned people
#                 tablita_people = list(col_values[0][40:])
#                 tablita_people = list(filter(None, tablita_people))
#                 people_access[sup] = tablita_people
#                 # st.warning(f"No departments have been assigned to this supervisor")
#             except:
#                 people_access[sup] = []

#     return current_supervisors, unassigned, dept_access, people_access


# current_supervisors, unassigned, dept_access, people_access = get_assigned_access()

# for i in dept_access.keys():
#     st.write(f"{i} has access to {dept_access.get(i)}")
