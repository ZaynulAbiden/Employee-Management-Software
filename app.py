import streamlit as st

import pandas as pd

import os

from datetime import datetime

import streamlit.components.v1 as components

from fpdf import FPDF

import base64



# ==========================================

# 1. APP CONFIGURATION & CONSTANTS

# ==========================================

st.set_page_config(

    page_title="Software District - HRMS & Payroll", 

    page_icon="💸",

    layout="wide",

    initial_sidebar_state="expanded"

)



# Dark Theme & Neon UI CSS

st.markdown("""

    <style>

    /* Main Background - Deep Slate */

    .stApp {

        background-color: #0f172a; 

    }



    /* Maximize Width for Wide Layout */

    .block-container {

        padding-left: 1rem !important;

        padding-right: 1rem !important;

        padding-top: 2rem !important;

        padding-bottom: 1rem !important;

        max-width: 100% !important;

    }

    

    /* Global Typography - Bright & Readable */

    h1 {

        color: #38bdf8 !important; /* Sky Blue */

        font-family: 'Inter', sans-serif;

        font-weight: 800 !important;

        font-size: 2.5rem !important;

        text-shadow: 0 0 15px rgba(56, 189, 248, 0.3);

        margin-bottom: 1rem !important;

    }

    h2 {

        color: #f8fafc !important; /* White/Slate 50 */

        font-family: 'Inter', sans-serif;

        font-weight: 700 !important;

        font-size: 1.8rem !important;

        border-bottom: 2px solid #334155;

        padding-bottom: 10px;

        margin-top: 1.5rem !important;

    }

    h3 {

        color: #94a3b8 !important; /* Slate 400 */

        font-size: 1.3rem !important;

    }

    p, label, span, div {

        color: #cbd5e1; /* Slate 300 */

        font-family: 'Inter', sans-serif;

    }

    

    /* Section Description Panels */

    .section-desc {

        background-color: #1e293b;

        border-left: 5px solid #38bdf8;

        color: #94a3b8;

        padding: 15px;

        border-radius: 0 8px 8px 0;

        margin-bottom: 20px;

        font-size: 0.95rem;

        box-shadow: 0 4px 6px rgba(0,0,0,0.2);

    }

    .section-desc strong {

        color: #38bdf8;

    }



    /* Cards/Containers */

    div.stVerticalBlock > div[data-testid="stVerticalBlockBorderWrapper"] {

        background-color: #1e293b !important; /* Slate 800 */

        border: 1px solid #334155 !important;

        border-radius: 12px !important;

        padding: 20px !important;

        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);

    }



    /* Input Fields */

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {

        background-color: #334155 !important; /* Slate 700 */

        color: #f8fafc !important; /* White Text */

        border: 1px solid #475569 !important;

        border-radius: 6px !important;

        min-height: 45px; /* Larger inputs */

    }

    .stTextInput input:focus, .stNumberInput input:focus {

        border-color: #38bdf8 !important;

        box-shadow: 0 0 0 1px #38bdf8 !important;

    }

    

    /* Strict Dropdown Styling */

    div[data-baseweb="select"] input {

        cursor: pointer !important;

        caret-color: transparent !important;

    }

    div[data-baseweb="select"] div {

        cursor: pointer !important;

    }



    div[data-baseweb="popover"] {

        background-color: #1e293b !important;

    }

    div[data-baseweb="select"] ul {

        background-color: #1e293b !important;

        color: white !important;

    }



    /* Tabs - EXPANDED WIDTH */

    .stTabs [data-baseweb="tab-list"] {

        background-color: #1e293b;

        padding: 10px 10px 0 10px;

        border-radius: 10px 10px 0 0;

        gap: 10px;

        border-bottom: 2px solid #334155;

        display: flex;

        width: 100%;

    }

    .stTabs [data-baseweb="tab-list"] button {

        background-color: transparent;

        border: none;

        color: #94a3b8;

        flex-grow: 1; /* Tabs take full width */

        text-align: center;

    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {

        background-color: #38bdf8 !important;

        border-radius: 6px 6px 0 0;

    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {

        color: #0f172a !important; /* Dark text on bright tab */

        font-weight: 800 !important;

        font-size: 1.1rem !important;

    }



    /* BUTTON STYLING - LARGER & BOLDER */

    .stButton > button {

        border-radius: 8px !important;

        font-weight: 700 !important;

        color: white !important;

        border: none !important;

        transition: transform 0.1s;

        height: 50px !important; /* Taller buttons */

        font-size: 16px !important;

    }

    .stButton > button:active {

        transform: scale(0.98);

    }

    

    /* Green Actions (Add, Save, Login, Confirm) */

    div[data-testid="stColumn"] button p:contains("Add"),

    div[data-testid="stColumn"] button p:contains("Save"),

    div[data-testid="stColumn"] button p:contains("Confirm"),

    div[data-testid="stColumn"] button p:contains("Login") {

        color: white !important;

    }

    div[data-testid="stColumn"] button:has(p:contains("Add")),

    div[data-testid="stColumn"] button:has(p:contains("Save")),

    div[data-testid="stColumn"] button:has(p:contains("Confirm")),

    div[data-testid="stColumn"] button:has(p:contains("Login")) {

        background-color: #10b981 !important; /* Emerald 500 */

        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);

    }



    /* Red Actions (Reset, Cancel, Sign Out, Delete) */

    div[data-testid="stColumn"] button p:contains("Reset"),

    div[data-testid="stColumn"] button p:contains("Cancel"),

    div[data-testid="stColumn"] button p:contains("Sign Out"),

    div[data-testid="stColumn"] button p:contains("Delete") {

        color: white !important;

    }

    div[data-testid="stColumn"] button:has(p:contains("Reset")),

    div[data-testid="stColumn"] button:has(p:contains("Cancel")),

    div[data-testid="stColumn"] button:has(p:contains("Sign Out")),

    div[data-testid="stColumn"] button:has(p:contains("Delete")) {

        background-color: #ef4444 !important; /* Red 500 */

        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.2);

    }

    

    /* Blue Actions (View, Edit, Sync) */

    div[data-testid="stColumn"] button:has(p:contains("View")),

    div[data-testid="stColumn"] button:has(p:contains("Edit")),

    div[data-testid="stColumn"] button:has(p:contains("Sync")) {

        background-color: #3b82f6 !important; /* Blue 500 */

        height: auto !important; /* Keep table buttons smaller */

        padding: 5px 15px !important;

        min-height: 0px !important;

    }



    /* Table Header Styling */

    .table-header {

        background-color: #334155;

        padding: 15px;

        border-radius: 8px;

        font-weight: 800;

        color: #38bdf8;

        border: 1px solid #475569;

        margin-bottom: 10px;

        text-transform: uppercase;

        letter-spacing: 0.5px;

        font-size: 0.9rem;

    }

    

    /* Custom Dataframe */

    [data-testid="stDataFrame"] {

        border: 1px solid #334155;

        border-radius: 8px;

    }

    </style>

    """, unsafe_allow_html=True)



EMPLOYEE_FILE = "employees.csv"

LOG_FILE = "audit_log.csv"

PAYROLL_FILE = "payroll_history.csv"

CONFIG_FILE = "config.csv"

ATTENDANCE_CONFIG_FILE = "attendance_config.csv"

DAILY_ATTENDANCE_FILE = "daily_attendance.csv"



USERS = {"zayn": "admin123"}

EMPLOYEE_TYPES = ["Full Time", "Part Time", "Hourly"]



# ==========================================

# 2. DATA MANAGEMENT LAYER

# ==========================================

def init_storage():

    if not os.path.exists(CONFIG_FILE):

        default_roles = ["Unity Developer", "QA Engineer", "3d Designer", "HR", "Production Manager", "CEO"]

        pd.DataFrame({"Roles": default_roles}).to_csv(CONFIG_FILE, index=False)



    if not os.path.exists(ATTENDANCE_CONFIG_FILE):

        default_rules = pd.DataFrame([

            {"Parameter": "Late", "Value": 10.0},

            {"Parameter": "Extra Late", "Value": 20.0},

            {"Parameter": "Half Day", "Value": 50.0},

            {"Parameter": "Absent", "Value": 100.0}

        ])

        default_rules.to_csv(ATTENDANCE_CONFIG_FILE, index=False)



    if not os.path.exists(DAILY_ATTENDANCE_FILE):

        pd.DataFrame(columns=["Date", "Employee ID", "Name", "Status"]).to_csv(DAILY_ATTENDANCE_FILE, index=False)



    required_columns = ["ID", "Name", "Role", "Employee Type", "Contact", "Status", "Currency", "Base Salary", "Joining Date"]

    

    if not os.path.exists(EMPLOYEE_FILE):

        df = pd.DataFrame([{

            "ID": 101, "Name": "Zayn Iftikhar", "Role": "CEO", "Employee Type": "Full Time",

            "Contact": "zayn@softwaredistrict.com", "Status": "Active",

            "Currency": "PKR", "Base Salary": 200000, "Joining Date": datetime.now().strftime("%Y-%m-%d")

        }])

        df.to_csv(EMPLOYEE_FILE, index=False)

    else:

        try:

            df = pd.read_csv(EMPLOYEE_FILE)

            changed = False

            defaults = {

                "Role": "Unity Developer", 

                "Employee Type": "Full Time",

                "Contact": "N/A", 

                "Status": "Active", 

                "Currency": "PKR", 

                "Joining Date": datetime.now().strftime("%Y-%m-%d")

            }

            for col in required_columns:

                if col not in df.columns:

                    df[col] = defaults.get(col, "")

                    changed = True

            if changed: df.to_csv(EMPLOYEE_FILE, index=False)

        except: pass



    if not os.path.exists(LOG_FILE):

        pd.DataFrame(columns=["Timestamp", "User", "Action", "Details"]).to_csv(LOG_FILE, index=False)



    if not os.path.exists(PAYROLL_FILE):

        pd.DataFrame(columns=[

            "Month", "Employee ID", "Name", "Base Salary", "Currency", 

            "Lates", "Extra Lates", "Half Days", "Absents", "Deductions", "Bonus", "Bonus Context", "Net Paid"

        ]).to_csv(PAYROLL_FILE, index=False)



def load_data(file): 

    try: return pd.read_csv(file)

    except: return pd.DataFrame()



def save_data(df, file): 

    df.to_csv(file, index=False)



def write_log(user, action, details):

    log_entry = pd.DataFrame([{"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "User": user, "Action": action, "Details": details}])

    log_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)



# ==========================================

# 3. CORE LOGIC

# ==========================================

def get_attendance_rules():

    df = load_data(ATTENDANCE_CONFIG_FILE)

    if df.empty: return {"Late": 10.0, "Extra Late": 20.0, "Half Day": 50.0, "Absent": 100.0}

    rules = df.set_index("Parameter")["Value"].to_dict()

    return {k: float(rules.get(k, v)) for k, v in [("Late", 10.0), ("Extra Late", 20.0), ("Half Day", 50.0), ("Absent", 100.0)]}



def calculate_net_salary(base, lates, extra_lates, half_days, absents, bonus):

    rules = get_attendance_rules()

    daily_wage = float(base) / 30

    total_deductions = (

        float(lates) * (daily_wage * (rules["Late"] / 100)) +

        float(extra_late_deduct := extra_lates) * (daily_wage * (rules["Extra Late"] / 100)) +

        float(half_days) * (daily_wage * (rules["Half Day"] / 100)) +

        float(absents) * (daily_wage * (rules["Absent"] / 100))

    )

    net = (float(base) + float(bonus)) - total_deductions

    return round(net, 2), round(total_deductions, 2)



# ==========================================

# 4. UI PAGES

# ==========================================



def render_login_page():

    _, col_mid, _ = st.columns([1, 1.5, 1])

    with col_mid:

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("<div style='text-align: center;'><h1>The Software District</h1><p style='color: #64748b;'>HRMS Enterprise Portal</p></div>", unsafe_allow_html=True)

        with st.container(border=True):

            user_i = st.text_input("Username").lower()

            pass_i = st.text_input("Password", type="password")

            if st.button("🔓 Login", use_container_width=True):

                if user_i in USERS and USERS[user_i] == pass_i:

                    st.session_state.authenticated = True

                    st.session_state.current_user = user_i

                    # Removed Write Log for Login

                    st.rerun()

                else: st.error("Invalid credentials")



def show_dashboard(emp_df):

    st.title("🚀 HRMS - Dashboard")

    st.markdown("""

        <div class="section-desc">

            <strong>System Overview</strong><br>

            Real-time metrics of the workforce and operational status.

        </div>

    """, unsafe_allow_html=True)



    t_count = len(emp_df) if not emp_df.empty else 0

    a_count = len(emp_df[emp_df['Status'] == 'Active']) if not emp_df.empty else 0

    d_count = len(emp_df[emp_df['Status'] == 'Deactive']) if not emp_df.empty else 0

    st.markdown(f"""

        <div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">

            <h3 style="color: #38bdf8 !important;">📈 Workforce Statistics</h3>

            <ul style="color: #cbd5e1; list-style-type: none; padding: 0;">

                <li style="margin-bottom: 10px;">👥 <b>Total Workforce:</b> {t_count} Records</li>

                <li style="margin-bottom: 10px;">✅ <b>Active Personnel:</b> {a_count} Employees</li>

                <li style="margin-bottom: 10px;">💤 <b>Inactive Records:</b> {d_count} Files</li>

            </ul>

        </div>

    """, unsafe_allow_html=True)



def show_daily_attendance(df):

    st.header("📅 Attendance Portal")

    st.markdown("""

        <div class="section-desc">

            <strong>Exception Management</strong><br>

            Log daily attendance exceptions such as Lates, Absents, or Half Days. Default status is 'Present'.

        </div>

    """, unsafe_allow_html=True)



    log_date = st.date_input("Select Date", datetime.now())

    date_str = log_date.strftime("%Y-%m-%d")

    active_emps = df[df['Status'] == 'Active'].copy()

    if active_emps.empty: st.warning("No active employees found."); return

    

    attendance_df = load_data(DAILY_ATTENDANCE_FILE)

    existing_logs = attendance_df[attendance_df['Date'] == date_str] if not attendance_df.empty else pd.DataFrame()

    

    updated_attendance = []

    with st.container(border=True):

        for _, row in active_emps.iterrows():

            default_status = "Present"

            if not existing_logs.empty:

                match = existing_logs[pd.to_numeric(existing_logs['Employee ID'], errors='coerce') == float(row['ID'])]

                if not match.empty: default_status = match.iloc[0]['Status']

            

            c1, c2 = st.columns([3, 1])

            c1.markdown(f"**{row['Name']}** <br><small style='color: #64748b;'>{row['Role']}</small>", unsafe_allow_html=True)

            status = c2.selectbox("Status", ["Present", "Late", "Extra Late", "Half Day", "Absent"], index=["Present", "Late", "Extra Late", "Half Day", "Absent"].index(default_status), key=f"att_{int(row['ID'])}")

            updated_attendance.append({"Date": date_str, "Employee ID": int(row['ID']), "Name": row['Name'], "Status": status})

            st.divider()



        if st.button("💾 Save Daily Log", use_container_width=True):

            if not attendance_df.empty: 

                attendance_df['Employee ID'] = pd.to_numeric(attendance_df['Employee ID'], errors='coerce')

                attendance_df = attendance_df[attendance_df['Date'] != date_str]

            attendance_df = pd.concat([attendance_df, pd.DataFrame(updated_attendance)], ignore_index=True)

            save_data(attendance_df, DAILY_ATTENDANCE_FILE)

            st.success(f"Log for {date_str} archived.")

            write_log(st.session_state.current_user, "Attendance", f"updated attendance for {date_str}")



def show_employee_management(df):

    st.header("👥 Employee Records")

    st.markdown("""

        <div class="section-desc">

            <strong>Personnel Management</strong><br>

            View active staff, update details, or onboard new employees into the system.

        </div>

    """, unsafe_allow_html=True)

    roles_df = load_data(CONFIG_FILE)

    roles_list = roles_df["Roles"].tolist() if not roles_df.empty else ["Unity Developer"]

    

    tab1, tab2 = st.tabs(["📋 Employee List", "➕ Onboard Employee"])

    

    if "edit_target_id" not in st.session_state: st.session_state.edit_target_id = None

    

    with tab1:

        # Search and Filter Logic

        c_search, c_filter = st.columns([2, 1])

        query = c_search.text_input("🔍 Quick Search (Name or ID)...", placeholder="Type to search...")

        status_filter = c_filter.multiselect("Filter Status", ["Active", "Deactive"], default=["Active"])

        

        display_df = df[df['Status'].isin(status_filter)]

        if query:

            display_df = display_df[display_df['Name'].str.contains(query, case=False) | display_df['ID'].astype(str).str.contains(query)]

        

        # Custom Table Design

        st.markdown("""

            <div class="table-header">

                <div style="display: flex; justify-content: space-between;">

                    <span style="flex: 0.5;">ID</span>

                    <span style="flex: 2;">Full Name</span>

                    <span style="flex: 1.5;">Designation</span>

                    <span style="flex: 1;">Type</span>

                    <span style="flex: 1;">Status</span>

                    <span style="flex: 1.2;">Joined</span>

                    <span style="flex: 1.2;">Salary</span>

                    <span style="flex: 0.8; text-align: right;">Action</span>

                </div>

            </div>

        """, unsafe_allow_html=True)

        

        for _, row in display_df.iterrows():

            with st.container():

                r_c1, r_c2, r_c3, r_c4, r_c5, r_c6, r_c7, r_c8 = st.columns([0.5, 2, 1.5, 1, 1, 1.2, 1.2, 0.8])

                r_c1.write(f"#{int(row['ID'])}")

                r_c2.write(f"**{row['Name']}**")

                r_c3.write(f"{row['Role']}")

                r_c4.write(f"{row.get('Employee Type', 'Full Time')}")

                

                # Status Logic with Color

                status_val = row['Status']

                status_color = "#4ade80" if status_val == "Active" else "#f87171" # Green if Active, Red if Deactive

                r_c5.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{status_val}</span>", unsafe_allow_html=True)

                

                r_c6.write(f"{row['Joining Date']}")

                r_c7.write(f"{row['Currency']} {row['Base Salary']:,.0f}")

                if r_c8.button("✏️ Edit", key=f"btn_edit_{row['ID']}", use_container_width=True):

                    st.session_state.edit_target_id = int(row['ID'])

                    st.rerun()

                st.divider()



        # Edit Portal Section

        if st.session_state.edit_target_id:

            st.markdown("---")

            st.subheader(f"🛠️ Updating: ID #{st.session_state.edit_target_id}")

            emp_subset = df[pd.to_numeric(df['ID'], errors='coerce') == st.session_state.edit_target_id]

            if not emp_subset.empty:

                ed = emp_subset.iloc[0]

                with st.container(border=True):

                    e_c1, e_c2 = st.columns(2)

                    up_name = e_c1.text_input("Full Name", value=ed['Name'])

                    up_role = e_c2.selectbox("Designation", roles_list, index=roles_list.index(ed['Role']) if ed['Role'] in roles_list else 0)

                    

                    e_c3, e_c4 = st.columns(2)

                    

                    # Joining Date Handling

                    try:

                        default_date = datetime.strptime(ed['Joining Date'], "%Y-%m-%d").date()

                    except:

                        default_date = datetime.now().date()

                        

                    up_type = e_c3.selectbox("Employee Type", EMPLOYEE_TYPES, index=EMPLOYEE_TYPES.index(ed.get('Employee Type', 'Full Time')) if ed.get('Employee Type', 'Full Time') in EMPLOYEE_TYPES else 0)

                    up_date = e_c4.date_input("Joining Date", value=default_date)



                    e_c5, e_c6, e_c7 = st.columns(3)

                    up_sal = e_c5.number_input("Base Salary", value=float(ed['Base Salary']))

                    up_curr = e_c6.selectbox("Currency", ["PKR", "USD"], index=0 if ed['Currency'] == "PKR" else 1)

                    up_stat = e_c7.selectbox("Status", ["Active", "Deactive"], index=0 if ed['Status'] == "Active" else 1)

                    

                    # Enhanced Button Layout

                    st.markdown("<br>", unsafe_allow_html=True)

                    btn_save, btn_cancel, btn_del = st.columns(3)

                    

                    with btn_save:

                        if st.button("💾 Save Changes", use_container_width=True):

                            # Detect changes for logging

                            changes = []

                            if up_sal != float(ed['Base Salary']): changes.append("Salary")

                            if up_role != ed['Role']: changes.append("Designation")

                            if up_stat != ed['Status']: changes.append("Status")

                            if up_type != ed.get('Employee Type', 'Full Time'): changes.append("Type")

                            

                            change_str = ", ".join(changes) if changes else "details"

                            

                            df.loc[pd.to_numeric(df['ID'], errors='coerce') == st.session_state.edit_target_id, 

                                   ['Name', 'Role', 'Employee Type', 'Joining Date', 'Base Salary', 'Currency', 'Status']] = \

                                   [up_name, up_role, up_type, up_date.strftime("%Y-%m-%d"), up_sal, up_curr, up_stat]

                            save_data(df, EMPLOYEE_FILE)

                            

                            # LOG: [admin] changed employee [name]'s salary etc

                            log_msg = f"changed employee [{up_name}]'s {change_str}"

                            write_log(st.session_state.current_user, "Update", log_msg)

                            

                            st.session_state.edit_target_id = None

                            st.success("Record updated successfully.")

                            st.rerun()

                            

                    with btn_cancel:

                        if st.button("❌ Cancel", use_container_width=True):

                            st.session_state.edit_target_id = None

                            st.rerun()

                            

                    with btn_del:

                        if st.button("🗑️ Delete Employee", use_container_width=True):

                            name_to_del = ed['Name']

                            df = df[pd.to_numeric(df['ID'], errors='coerce') != st.session_state.edit_target_id]

                            save_data(df, EMPLOYEE_FILE)

                            

                            # LOG: [admin] deleted employee [name]

                            write_log(st.session_state.current_user, "Delete", f"deleted employee [{name_to_del}]")

                            

                            st.session_state.edit_target_id = None

                            st.warning("Employee record deleted.")

                            st.rerun()



    with tab2:

        with st.container(border=True):

            st.subheader("New Personnel Onboarding")

            

            f_col1, f_col2 = st.columns(2)

            with f_col1:

                new_name = st.text_input("Full Name", placeholder="e.g. Hassan Ali", key="onboard_name")

                new_role = st.selectbox("Designation", roles_list, key="onboard_role")

            

            with f_col2:

                new_type = st.selectbox("Employee Type", EMPLOYEE_TYPES, key="onboard_type")

                new_date = st.date_input("Joining Date", datetime.now(), key="onboard_date")



            f_col3, f_col4 = st.columns(2)

            with f_col3:

                new_curr = st.selectbox("Salary Currency", ["PKR", "USD"], key="onboard_curr")

            with f_col4:

                new_sal = st.number_input("Monthly Salary", min_value=0.0, step=1000.0, key="onboard_sal")

            

            st.markdown("<br>", unsafe_allow_html=True)

            btn_c1, btn_c2, btn_sp = st.columns([1.2, 1, 3])

            

            if btn_c1.button("➕ Add Employee", use_container_width=True):

                if not new_name:

                    st.error("Missing Info: Full Name is required.")

                elif new_name in df['Name'].values:

                    st.error(f"Duplicate Record: '{new_name}' already exists in the system.")

                else:

                    max_id = int(df["ID"].max() + 1) if not df.empty else 101

                    new_entry = pd.DataFrame([{

                        "ID": max_id, 

                        "Name": new_name, 

                        "Role": new_role, 

                        "Employee Type": new_type,

                        "Status": "Active", 

                        "Currency": new_curr, 

                        "Base Salary": new_sal, 

                        "Joining Date": new_date.strftime("%Y-%m-%d"), 

                        "Contact": "N/A"

                    }])

                    save_data(pd.concat([df, new_entry], ignore_index=True), EMPLOYEE_FILE)

                    

                    # LOG: [admin] created new employee [name]

                    write_log(st.session_state.current_user, "Create", f"created new employee [{new_name}]")

                    

                    st.success(f"Success! {new_name} has been onboarded.")

                    st.rerun()



            if btn_c2.button("🔄 Reset", use_container_width=True):

                st.rerun()



# ==========================================

# 5. PDF & PAYROLL LOGIC

# ==========================================

def generate_pdf(data, role, jd, rules):

    try:

        pdf = FPDF()

        pdf.set_auto_page_break(auto=False)

        pdf.add_page()

        pdf.set_margin(15)

        

        pdf.set_font("helvetica", "B", 18)

        pdf.cell(0, 10, "THE SOFTWARE DISTRICT", ln=True, align="C")

        pdf.set_font("helvetica", "B", 12)

        pdf.cell(0, 8, f"SALARY SLIP - {str(data['Month'])}", ln=True, align="C")

        pdf.line(15, 30, 195, 30)

        pdf.ln(5)

        

        pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(240, 240, 240)

        pdf.cell(0, 8, " EMPLOYEE INFORMATION", border=1, ln=True, fill=True)

        

        pdf.set_font("helvetica", "B", 9); pdf.set_fill_color(255, 255, 255)

        pdf.cell(40, 8, " Employee ID:", border="LTB")

        pdf.set_font("helvetica", "", 9)

        pdf.cell(50, 8, f"#{int(float(data['Employee ID']))}", border="TB")

        pdf.set_font("helvetica", "B", 9)

        pdf.cell(40, 8, " Full Name:", border="LTB")

        pdf.set_font("helvetica", "", 9)

        pdf.cell(50, 8, str(data['Name']), border="TRB", ln=True)

        

        pdf.set_font("helvetica", "B", 9)

        pdf.cell(40, 8, " Joining Date:", border="LTB")

        pdf.set_font("helvetica", "", 9)

        pdf.cell(50, 8, str(jd), border="TB")

        pdf.set_font("helvetica", "B", 9)

        pdf.cell(40, 8, " Designation:", border="LTB")

        pdf.set_font("helvetica", "", 9)

        pdf.cell(50, 8, str(role), border="TRB", ln=True)

        

        pdf.set_font("helvetica", "B", 9)

        pdf.cell(40, 8, " Monthly Base:", border="LTB")

        pdf.set_font("helvetica", "", 9)

        pdf.cell(50, 8, f"{float(data['Base Salary']):,.0f}", border="TB")

        pdf.set_font("helvetica", "B", 9)

        pdf.cell(40, 8, " Currency Unit:", border="LTB")

        pdf.set_font("helvetica", "", 9)

        pdf.cell(50, 8, str(data['Currency']), border="TRB", ln=True)

        

        pdf.ln(10)

        

        pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(240, 240, 240)

        pdf.cell(130, 8, " EARNINGS COMPONENTS", border=1, fill=True)

        pdf.cell(50, 8, f" AMOUNT ({str(data['Currency'])})", border=1, fill=True, align="R"); pdf.ln()

        

        pdf.set_font("helvetica", "", 9)

        pdf.cell(130, 8, " Monthly Standard Salary", border="LRB")

        pdf.cell(50, 8, f"{float(data['Base Salary']):,.2f}", border="RB", align="R"); pdf.ln()

        

        ctx = str(data['Bonus Context']) if pd.notna(data['Bonus Context']) and str(data['Bonus Context']).lower() != "nan" else "Regular"

        pdf.cell(130, 8, f" Bonus / Incentives ({ctx})", border="LRB")

        pdf.cell(50, 8, f"{float(data['Bonus']):,.2f}", border="RB", align="R"); pdf.ln()

        

        pdf.ln(6)

        

        pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(240, 240, 240)

        pdf.cell(130, 8, " ATTENDANCE DEDUCTIONS", border=1, fill=True)

        pdf.cell(50, 8, " AMOUNT", border=1, fill=True, align="R"); pdf.ln()

        

        daily_wage = float(data['Base Salary']) / 30

        deductions = [("Lates", float(data['Lates']), "Late"), ("Extra Lates", float(data['Extra Lates']), "Extra Late"), ("Half Days", float(data['Half Days']), "Half Day"), ("Absents", float(data['Absents']), "Absent")]

        

        for label, days, key in deductions:

            x_start = pdf.get_x()

            y_start = pdf.get_y()

            pdf.rect(x_start, y_start, 130, 11) 

            pdf.set_font("helvetica", "B", 9)

            pdf.set_xy(x_start + 2, y_start + 1.5)

            pdf.cell(120, 4, f"{label} ({int(days)} days)", ln=False)

            rate = float(rules[key])

            pdf.set_font("helvetica", "I", 8); pdf.set_text_color(120, 120, 120)

            pdf.set_xy(x_start + 2, y_start + 5.5)

            pdf.cell(120, 3, f"{rate}% pay of the day", ln=False)

            pdf.set_font("helvetica", "", 9); pdf.set_text_color(0, 0, 0)

            pdf.set_xy(x_start + 130, y_start)

            amt = days * daily_wage * (rate / 100)

            pdf.cell(50, 11, f" - {amt:,.2f}", border=1, align="R")

            pdf.set_xy(x_start, y_start + 11)



        pdf.ln(5)

        pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(15, 23, 42); pdf.set_text_color(255, 255, 255)

        pdf.cell(130, 12, " TOTAL NET PAYABLE", border=1, fill=True)

        pdf.cell(50, 12, f" {str(data['Currency'])} {float(data['Net Paid']):,.2f}", border=1, fill=True, align="R")

        

        pdf.set_y(260)

        pdf.set_font("helvetica", "I", 8); pdf.set_text_color(150, 150, 150)

        pdf.cell(0, 4, "Official Proof of Payment - Generated by SD HRMS.", ln=True, align="C")

        pdf.cell(0, 4, "Strictly Confidential Document.", ln=True, align="C")

        

        return bytes(pdf.output())

    except Exception as e:

        raise e



def open_pdf_js(pdf_bytes):

    b64 = base64.b64encode(pdf_bytes).decode()

    js = f"""<script>var pdfWindow = window.open(""); if (pdfWindow) {{ pdfWindow.document.write("<html><head><title>Salary Slip</title></head><body style='margin:0; padding:0;'><iframe width='100%' height='100%' style='border:none;' src='data:application/pdf;base64,{b64}'></iframe></body></html>"); }} else {{ alert("Popup blocked!"); }}</script>"""

    components.html(js, height=0)



def show_payroll_management(emp_df):

    st.header("💳 Monthly Payroll")

    st.markdown("""

        <div class="section-desc">

            <strong>Salary Processing Center</strong><br>

            Calculate and finalize salaries. Syncs with attendance logs to automatically calculate deductions.

        </div>

    """, unsafe_allow_html=True)

    c_m, c_y = st.columns(2)

    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    now = datetime.now()

    month = c_m.selectbox("Processing Month", month_names, index=now.month - 1)

    year = c_y.selectbox("Processing Year", [2024, 2025, 2026], index=[2024, 2025, 2026].index(now.year))

    period = f"{month} {year}"

    

    attendance_df = load_data(DAILY_ATTENDANCE_FILE)

    payroll_history = load_data(PAYROLL_FILE)

    active_emps = emp_df[emp_df['Status'] == 'Active'].copy()

    if active_emps.empty: st.warning("No active employees found."); return



    if st.button("🔄 Sync Attendance Records", use_container_width=True):

        m_idx = month_names.index(month) + 1

        if not attendance_df.empty:

            attendance_df['ParsedDate'] = pd.to_datetime(attendance_df['Date'], errors='coerce')

            attendance_df['Employee ID'] = pd.to_numeric(attendance_df['Employee ID'], errors='coerce')

            month_logs = attendance_df[(attendance_df['ParsedDate'].dt.year == year) & (attendance_df['ParsedDate'].dt.month == m_idx)]

            for _, row in active_emps.iterrows():

                eid_key = int(row['ID'])

                emp_logs = month_logs[month_logs['Employee ID'] == float(row['ID'])]

                st.session_state[f"l_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Late"]))

                st.session_state[f"el_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Extra Late"]))

                st.session_state[f"hd_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Half Day"]))

                st.session_state[f"ab_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Absent"]))

            st.toast(f"Sync Complete for {period}"); st.rerun()



    payroll_buffer = []

    with st.container(border=True):

        for _, row in active_emps.iterrows():

            eid_key = int(row['ID'])

            for k in ['l', 'el', 'hd', 'ab']:

                if f"{k}_{eid_key}" not in st.session_state: st.session_state[f"{k}_{eid_key}"] = 0



            c_head, c_btn = st.columns([4, 1.2])

            c_head.markdown(f"#### {row['Name']} — <span style='color: #64748b;'>{row['Role']}</span>", unsafe_allow_html=True)

            hist_match = payroll_history[(payroll_history['Month'] == period) & (pd.to_numeric(payroll_history['Employee ID'], errors='coerce') == float(row['ID']))]

            if not hist_match.empty:

                if c_btn.button("📄 View Slip", key=f"view_{eid_key}", use_container_width=True):

                    pdf_bytes = generate_pdf(hist_match.iloc[0], row['Role'], row['Joining Date'], get_attendance_rules())

                    open_pdf_js(pdf_bytes)

            else: c_btn.info("Pending Process")

            

            p_cols = st.columns(4)

            l = p_cols[0].number_input("Late", min_value=0, key=f"l_{eid_key}")

            el = p_cols[1].number_input("Extra Late", min_value=0, key=f"el_{eid_key}")

            hd = p_cols[2].number_input("Half Day", min_value=0, key=f"hd_{eid_key}")

            ab = p_cols[3].number_input("Absent", min_value=0, key=f"ab_{eid_key}")

            

            b_cols = st.columns(2)

            bonus = b_cols[0].number_input("Bonus/Extra", min_value=0.0, key=f"bon_{eid_key}")

            ctx = b_cols[1].text_input("Reason", placeholder="Reward context...", key=f"ctx_{eid_key}")

            

            net, deduct = calculate_net_salary(row['Base Salary'], l, el, hd, ab, bonus)

            payroll_buffer.append({"Month": period, "Employee ID": row['ID'], "Name": row['Name'], "Base Salary": row['Base Salary'], "Currency": row['Currency'], "Lates": l, "Extra Lates": el, "Half Days": hd, "Absents": ab, "Deductions": deduct, "Bonus": bonus, "Bonus Context": ctx, "Net Paid": net})

            st.divider()



    if st.button("🚀 Confirm & Process Payroll", use_container_width=True):

        if not payroll_history.empty:

            payroll_history['Employee ID'] = pd.to_numeric(payroll_history['Employee ID'], errors='coerce')

            payroll_history = payroll_history[~((payroll_history['Month'] == period) & (payroll_history['Employee ID'].isin([float(p['Employee ID']) for p in payroll_buffer])))]

        save_data(pd.concat([payroll_history, pd.DataFrame(payroll_buffer)], ignore_index=True), PAYROLL_FILE)

        st.success(f"Payroll archived for {period}."); st.rerun()



# ==========================================

# 6. CONFIGURATION

# ==========================================

def show_config():

    st.header("⚙️ Enterprise Configuration")

    t1, t2 = st.tabs(["📋 Designation Management", "⚖️ Deduction Policy"])

    

    with t1:

        st.markdown("""

            <div class="section-desc">

                <strong>Job Titles</strong><br>

                Define the roles available in your organization. These appear in onboarding dropdowns.

            </div>

        """, unsafe_allow_html=True)

        roles_df = load_data(CONFIG_FILE)

        c1, c2 = st.columns([4, 1.2])

        new_r = c1.text_input("New Designation Title", placeholder="Enter job title...", label_visibility="collapsed")

        if c2.button("✨ Add Role"):

            if new_r: save_data(pd.concat([roles_df, pd.DataFrame({"Roles": [new_r]})], ignore_index=True), CONFIG_FILE); st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        upd_roles = st.data_editor(roles_df, use_container_width=True, num_rows="dynamic", key="role_ed")

        if st.button("💾 Save Official Registry"): save_data(upd_roles, CONFIG_FILE); st.rerun()



    with t2:

        st.markdown("""

            <div class="section-desc">

                <strong>Financial Penalties</strong><br>

                Configure the percentage of daily wage deducted for specific attendance exceptions.

            </div>

        """, unsafe_allow_html=True)

        att_df = load_data(ATTENDANCE_CONFIG_FILE)

        upd = st.data_editor(att_df, use_container_width=True, column_config={"Parameter": st.column_config.TextColumn("Exception Category", disabled=True), "Value": st.column_config.NumberColumn("% of Deduction", format="%d%%")}, key="policy_ed")

        if st.button("💾 Apply Global Updates"): save_data(upd, ATTENDANCE_CONFIG_FILE); st.rerun()



# ==========================================

# 7. MAIN ROUTING

# ==========================================

def main():

    init_storage()

    if "authenticated" not in st.session_state: st.session_state.authenticated = False

    if not st.session_state.authenticated: render_login_page()

    else:

        with st.sidebar:

            st.title("SD - HRMS"); st.markdown(f"**Admin:** {st.session_state.current_user}"); st.divider()

            page = st.radio("Navigation", ["Dashboard", "Employee Records", "Daily Attendance", "Payroll Management", "Configuration", "Audit Logs"])

            if st.button("🚪 Sign Out Session", use_container_width=True): st.session_state.authenticated = False; st.rerun()

        emp_df = load_data(EMPLOYEE_FILE)

        if page == "Dashboard": show_dashboard(emp_df)

        elif page == "Employee Records": show_employee_management(emp_df)

        elif page == "Daily Attendance": show_daily_attendance(emp_df)

        elif page == "Payroll Management": show_payroll_management(emp_df)

        elif page == "Configuration": show_config()

        elif page == "Audit Logs":

            st.title("📜 Audit Trail")

            

            c_clear, c_space = st.columns([1, 4])

            if c_clear.button("🗑️ Delete All Logs", use_container_width=True):

                # Clear logs by rewriting file with empty df

                pd.DataFrame(columns=["Timestamp", "User", "Action", "Details"]).to_csv(LOG_FILE, index=False)

                st.success("All logs have been cleared.")

                st.rerun()

            

            logs = load_data(LOG_FILE)

            if not logs.empty:

                # Format for display: [User] Details

                display_logs = logs.copy()

                display_logs['Log Entry'] = display_logs.apply(lambda x: f"[{x['User']}] {x['Details']}", axis=1)

                st.dataframe(display_logs[['Timestamp', 'Log Entry']].iloc[::-1], use_container_width=True)

            else:

                st.info("No audit logs available.")



if __name__ == "__main__": main()