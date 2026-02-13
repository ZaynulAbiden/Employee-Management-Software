import streamlit as st
import pandas as pd
import os
from datetime import datetime, time
import streamlit.components.v1 as components
from fpdf import FPDF
import base64

# ==========================================
# 1. APP CONFIGURATION & CONSTANTS
# ==========================================
st.set_page_config(
    page_title="Software District - HRMS", 
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
        min-height: 45px;
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

    /* UNIFORM SIDEBAR BUTTON STYLE */
    [data-testid="stSidebar"] .stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        color: white !important;
        border: none !important;
        transition: all 0.2s ease-in-out;
        height: 45px !important;
        font-size: 15px !important;
        background-color: #3b82f6 !important; /* Default Blue */
        margin-bottom: 5px !important;
        text-align: left !important;
        padding-left: 20px !important;
    }
    
    /* Highlighted / Active Button Style */
    div.active-nav .stButton > button {
        background-color: #10b981 !important; /* Emerald Green for Active */
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        border-left: 5px solid white !important;
    }

    /* Logout / Specific Red Actions */
    [data-testid="stSidebar"] .stButton > button:contains("Sign Out") {
        background-color: #ef4444 !important;
        margin-top: 20px !important;
    }

    /* Main Page Action Buttons */
    div[data-testid="stColumn"] button:has(p:contains("Add")),
    div[data-testid="stColumn"] button:has(p:contains("Save")),
    div[data-testid="stColumn"] button:has(p:contains("Confirm")),
    div[data-testid="stColumn"] button:has(p:contains("Mark Presence")),
    div[data-testid="stColumn"] button:has(p:contains("Update Password")) {
        background-color: #10b981 !important;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
    }
    
    div[data-testid="stColumn"] button:has(p:contains("Delete")),
    div[data-testid="stColumn"] button:has(p:contains("Cancel")),
    div[data-testid="stColumn"] button:has(p:contains("Reset")) {
        background-color: #ef4444 !important;
    }

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
    </style>
    """, unsafe_allow_html=True)

EMPLOYEE_FILE = "employees.csv"
LOG_FILE = "audit_log.csv"
PAYROLL_FILE = "payroll_history.csv"
CONFIG_FILE = "config.csv"
ATTENDANCE_CONFIG_FILE = "attendance_config.csv"
DAILY_ATTENDANCE_FILE = "daily_attendance.csv"
TIME_POLICY_FILE = "time_policy.csv"

# Admin fallback
ADMIN_USERS = {"zayn": "123"}
EMPLOYEE_TYPES = ["Full Time", "Part Time", "Hourly"]

# ==========================================
# 2. DATA MANAGEMENT LAYER
# ==========================================
def init_storage():
    if not os.path.exists(CONFIG_FILE):
        default_roles = ["Unity Developer", "QA Engineer", "3d Designer", "HR", "Production Manager", "CEO"]
        pd.DataFrame({"Roles": default_roles}).to_csv(CONFIG_FILE, index=False)

    if not os.path.exists(TIME_POLICY_FILE):
        default_times = pd.DataFrame([
            {"Category": "Present", "Start": "09:00", "End": "09:30"},
            {"Category": "Late", "Start": "09:31", "End": "11:00"},
            {"Category": "Extra Late", "Start": "11:01", "End": "12:30"},
            {"Category": "Half Day", "Start": "12:31", "End": "14:00"}
        ])
        default_times.to_csv(TIME_POLICY_FILE, index=False)

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

    required_columns = ["ID", "Name", "Role", "Employee Type", "Status", "Currency", "Base Salary", "Joining Date", "Email", "Password"]
    
    if not os.path.exists(EMPLOYEE_FILE):
        df = pd.DataFrame(columns=required_columns)
        df.to_csv(EMPLOYEE_FILE, index=False)
    else:
        try:
            df = pd.read_csv(EMPLOYEE_FILE)
            changed = False
            defaults = {"Role": "Employee", "Employee Type": "Full Time", "Status": "Active", "Currency": "PKR", "Joining Date": datetime.now().strftime("%Y-%m-%d"), "Email": "N/A", "Password": "123"}
            if "Contact" in df.columns:
                df = df.drop(columns=["Contact"])
                changed = True
            for col in required_columns:
                if col not in df.columns:
                    df[col] = defaults.get(col, "123")
                    changed = True
            if changed: df.to_csv(EMPLOYEE_FILE, index=False)
        except: pass

    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=["Timestamp", "User", "Action", "Details"]).to_csv(LOG_FILE, index=False)

    if not os.path.exists(PAYROLL_FILE):
        pd.DataFrame(columns=["Month", "Employee ID", "Name", "Base Salary", "Currency", "Lates", "Extra Lates", "Half Days", "Absents", "Deductions", "Bonus", "Bonus Context", "Net Paid"]).to_csv(PAYROLL_FILE, index=False)

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

def get_detailed_status_info():
    """Returns (status, deduction_pct, state_code) based on current time.
    state_code: 'EARLY', 'IN_WINDOW', 'ABSENT'
    """
    policy = load_data(TIME_POLICY_FILE)
    deductions = get_attendance_rules()
    if policy.empty: return "Absent", 100.0, "ABSENT"
    
    now_time = datetime.now().time()
    
    first_start = datetime.strptime(policy.iloc[0]['Start'], "%H:%M").time()
    last_end = datetime.strptime(policy.iloc[-1]['End'], "%H:%M").time()
    
    if now_time < first_start:
        return "Early Arrival", 0.0, "EARLY"
    
    if now_time > last_end:
        return "Absent", 100.0, "ABSENT"
        
    for _, row in policy.iterrows():
        try:
            start_t = datetime.strptime(row['Start'], "%H:%M").time()
            end_t = datetime.strptime(row['End'], "%H:%M").time()
            
            if start_t <= now_time <= end_t:
                cat = row['Category']
                pct = deductions.get(cat, 0.0) if cat != "Present" else 0.0
                return cat, pct, "IN_WINDOW"
        except: continue
            
    return "Absent", 100.0, "ABSENT"

# ==========================================
# 4. UI PAGES
# ==========================================

def render_login_page():
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'><h1>The Software District</h1><p style='color: #64748b;'>HRMS Enterprise Portal</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            user_i = st.text_input("Email / Username").lower().strip()
            pass_i = st.text_input("Password", type="password")
            if st.button("🔓 Login", use_container_width=True):
                if user_i in ADMIN_USERS and ADMIN_USERS[user_i] == pass_i:
                    st.session_state.authenticated = True
                    st.session_state.current_user = user_i
                    st.session_state.user_role = "Admin"
                    st.session_state.user_designation = "System Administrator"
                    st.session_state.current_page = "Dashboard"
                    st.toast(f"Welcome back, Administrator! 👋", icon="🚀")
                    st.rerun()
                
                emp_df = load_data(EMPLOYEE_FILE)
                if not emp_df.empty:
                    match = emp_df[(emp_df['Email'].str.lower() == user_i) & (emp_df['Password'].astype(str) == str(pass_i))]
                    if not match.empty:
                        user_data = match.iloc[0]
                        if user_data['Status'] == 'Active':
                            st.session_state.authenticated = True
                            st.session_state.current_user = user_data['Name']
                            st.session_state.current_email = user_data['Email']
                            st.session_state.user_id = int(user_data['ID'])
                            st.session_state.user_role = "Employee"
                            st.session_state.user_designation = user_data['Role']
                            st.session_state.current_page = "Dashboard"
                            st.toast(f"Welcome back, {user_data['Name']}! 👋", icon="🚀")
                            st.rerun()
                        else: st.error("Account is deactivated.")
                    else: st.error("Invalid credentials")
                else: st.error("Invalid credentials")

def show_profile_settings():
    st.title("👤 Profile Settings")
    st.markdown("""<div class="section-desc"><strong>User Account Details</strong><br>View your professional information and update your system password.</div>""", unsafe_allow_html=True)

    if st.session_state.user_role == "Admin":
        st.info("System Administrator credentials are hardcoded. Passwords cannot be updated via this UI.")
        return

    emp_df = load_data(EMPLOYEE_FILE)
    current_email = st.session_state.current_email
    user_row = emp_df[emp_df['Email'] == current_email].iloc[0]

    with st.container(border=True):
        st.subheader("Your Information")
        c1, c2 = st.columns(2)
        c1.text_input("Full Name", value=user_row['Name'], disabled=True)
        c2.text_input("Email", value=user_row['Email'], disabled=True)
        c1.text_input("Designation", value=user_row['Role'], disabled=True)
        c2.text_input("Employee Type", value=user_row['Employee Type'], disabled=True)
        
        st.divider()
        st.subheader("Update Password")
        old_pass = st.text_input("Current Password", type="password")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm New Password", type="password")
        
        if st.button("💾 Update Password", use_container_width=True):
            if old_pass != str(user_row['Password']): st.error("Incorrect current password.")
            elif new_pass != confirm_pass: st.error("Passwords do not match.")
            elif len(new_pass) < 3: st.error("Password too short.")
            else:
                emp_df.loc[emp_df['Email'] == current_email, 'Password'] = str(new_pass)
                save_data(emp_df, EMPLOYEE_FILE)
                write_log(st.session_state.current_user, "Security", "changed their password")
                st.toast("Password updated!", icon="✅")
                st.success("Your password has been changed successfully.")

def show_dashboard(emp_df):
    st.title("🚀 Software District HRMS - Dashboard")
    st.markdown("""<div class="section-desc"><strong>Real-time Overview</strong><br>Operational statistics and workforce status.</div>""", unsafe_allow_html=True)
    
    attendance_df = load_data(DAILY_ATTENDANCE_FILE)
    date_today = datetime.now().strftime("%Y-%m-%d")

    if st.session_state.user_role == "Admin":
        t_count = len(emp_df) if not emp_df.empty else 0
        a_count = len(emp_df[emp_df['Status'] == 'Active']) if not emp_df.empty else 0
        d_count = len(emp_df[emp_df['Status'] == 'Deactive']) if not emp_df.empty else 0
        st.markdown(f"""<div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;"><h3 style="color: #38bdf8 !important;">📈 Statistics</h3><ul><li>👥 <b>Workforce:</b> {t_count}</li><li>✅ <b>Active:</b> {a_count}</li><li>💤 <b>Inactive:</b> {d_count}</li></ul></div>""", unsafe_allow_html=True)
    else:
        user_id = st.session_state.user_id
        marked_today = attendance_df[(attendance_df['Date'] == date_today) & (pd.to_numeric(attendance_df['Employee ID'], errors='coerce') == user_id)]
        
        if marked_today.empty:
            status_preview, pct, state = get_detailed_status_info()
            if state == "EARLY":
                st.info("⏰ It's a bit early! The attendance window hasn't opened yet. Check back soon.")
            elif state == "ABSENT":
                st.error("⚠️ ALERT: You have missed the attendance windows. You are marked as **Absent** for today.")
            else:
                st.error(f"⚠️ ALERT: You have not marked your attendance for today! If you mark now, status will be: **{status_preview}** ({pct}% daily wage deduction).")
        else:
            final_status = marked_today.iloc[0]['Status']
            if final_status == "Absent":
                st.error("⚠️ ALERT: Attendance window is closed. You are marked as **Absent** for today.")
            else:
                st.success(f"✅ Attendance recorded for today as **{final_status}**. Checklist Done!")

        st.markdown(f"""<div style="background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;"><h3 style="color: #38bdf8 !important;">Welcome, {st.session_state.current_user}</h3><p>Mark your daily presence using the side menu.</p></div>""", unsafe_allow_html=True)

def show_daily_attendance(df):
    st.title("📅 Attendance Portal")
    date_today = datetime.now().strftime("%Y-%m-%d")
    attendance_df = load_data(DAILY_ATTENDANCE_FILE)

    if st.session_state.user_role == "Admin":
        st.markdown("""<div class="section-desc"><strong>Enterprise Attendance</strong><br>Default status is 'Absent'. Those who marked presence will appear as 'Present'.</div>""", unsafe_allow_html=True)
        log_date = st.date_input("Select Date", datetime.now())
        date_str = log_date.strftime("%Y-%m-%d")
        active_emps = df[df['Status'] == 'Active'].copy().sort_values(by="Name")
        if active_emps.empty: st.warning("No active employees found."); return
        existing_logs = attendance_df[attendance_df['Date'] == date_str] if not attendance_df.empty else pd.DataFrame()
        updated_attendance = []
        with st.container(border=True):
            for _, row in active_emps.iterrows():
                default_status = "Absent"
                if not existing_logs.empty:
                    match = existing_logs[pd.to_numeric(existing_logs['Employee ID'], errors='coerce') == float(row['ID'])]
                    if not match.empty: default_status = match.iloc[0]['Status']
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"""<div style='margin-bottom: 10px;'><strong style='font-size: 1.15rem; color: #f8fafc;'>{row['Name']}</strong><br><span style='color: #94a3b8; font-size: 0.9rem;'>{row['Role']}</span><br><span style='color: #38bdf8; font-size: 0.85rem;'>{row.get('Employee Type', 'Full Time')}</span></div>""", unsafe_allow_html=True)
                status = c2.selectbox("Status", ["Present", "Late", "Extra Late", "Half Day", "Absent"], index=["Present", "Late", "Extra Late", "Half Day", "Absent"].index(default_status), key=f"att_{int(row['ID'])}")
                updated_attendance.append({"Date": date_str, "Employee ID": int(row['ID']), "Name": row['Name'], "Status": status})
                st.divider()
            if st.button("💾 Save Daily Log", use_container_width=True):
                if not attendance_df.empty: attendance_df = attendance_df[attendance_df['Date'] != date_str]
                attendance_df = pd.concat([attendance_df, pd.DataFrame(updated_attendance)], ignore_index=True)
                save_data(attendance_df, DAILY_ATTENDANCE_FILE); st.toast("Saved!", icon="✅"); write_log(st.session_state.current_user, "Attendance", f"updated {date_str}")
    else:
        # EMPLOYEE VIEW
        st.markdown("""<div class="section-desc"><strong>Mark Your Presence</strong><br>Status is automatically determined based on system time and policy. Fallback to Absent if windows missed.</div>""", unsafe_allow_html=True)
        
        # Policy Reference Table for Employee
        with st.expander("🕒 View Attendance Policy Reference", expanded=False):
            st.markdown("### Organizational Attendance Windows")
            time_policy = load_data(TIME_POLICY_FILE)
            deduct_rules = get_attendance_rules()
            
            ref_data = []
            for _, r in time_policy.iterrows():
                cat = r['Category']
                deduct = f"{int(deduct_rules.get(cat, 0))}%" if cat != "Present" else "None"
                ref_data.append({"Category": cat, "Window": f"{r['Start']} to {r['End']}", "Deduction": deduct})
            
            st.table(pd.DataFrame(ref_data))

        user_id, user_name = st.session_state.user_id, st.session_state.current_user
        existing_log = attendance_df[(attendance_df['Date'] == date_today) & (pd.to_numeric(attendance_df['Employee ID'], errors='coerce') == user_id)]
        
        status_to_be, deduct_pct, state = get_detailed_status_info()

        if not existing_log.empty: 
            status_now = existing_log.iloc[0]['Status']
            if status_now == "Absent":
                st.error("Attendance window closed. You have been marked as **Absent** for today.")
            else:
                st.info(f"Your status for today is marked as: **{status_now}**")
        elif state == "EARLY":
            st.info("⏰ Too early! The marking window opens at the first scheduled slot.")
        elif state == "ABSENT":
            st.error("Attendance window closed. You have been marked as **Absent** for today.")
        else:
            st.warning("You have not yet marked your presence for today.")

        with st.container(border=True):
            st.subheader(f"Marking for: {date_today}")
            st.markdown(f"Current System Time: **{datetime.now().strftime('%H:%M')}**")
            
            if state == "EARLY":
                st.button("📍 Mark Presence", disabled=True, use_container_width=True, help="It's too early to mark attendance.")
            elif state == "ABSENT":
                st.markdown("Status: <strong style='color: #ef4444;'>ABSENT (Window Closed)</strong>", unsafe_allow_html=True)
                st.button("📍 Mark Presence", disabled=True, use_container_width=True)
            else:
                st.markdown(f"Status to be assigned: <strong style='color: #38bdf8;'>{status_to_be}</strong>", unsafe_allow_html=True)
                st.markdown(f"Deduction penalty: **{int(deduct_pct)}% of daily wage**")
                if st.button("📍 Mark Presence", use_container_width=True):
                    if not attendance_df.empty:
                        attendance_df = attendance_df[~((attendance_df['Date'] == date_today) & (pd.to_numeric(attendance_df['Employee ID'], errors='coerce') == user_id))]
                    new_row = pd.DataFrame([{"Date": date_today, "Employee ID": user_id, "Name": user_name, "Status": status_to_be}])
                    attendance_df = pd.concat([attendance_df, new_row], ignore_index=True)
                    save_data(attendance_df, DAILY_ATTENDANCE_FILE)
                    st.toast(f"Marked as {status_to_be}!", icon="✅")
                    write_log(st.session_state.current_user, "Attendance", f"marked self as {status_to_be}")
                    st.rerun()

def show_employee_management(df):
    st.title("👥 Employee Records")
    st.markdown("""<div class="section-desc"><strong>Personnel Management</strong><br>Manage staff. Email is used for login.</div>""", unsafe_allow_html=True)
    roles_df = load_data(CONFIG_FILE); roles_list = roles_df["Roles"].tolist() if not roles_df.empty else ["Unity Developer"]
    tab1, tab2 = st.tabs(["📋 Employee List", "➕ Onboard Employee"])
    if "edit_target_id" not in st.session_state: st.session_state.edit_target_id = None
    if "confirm_delete" not in st.session_state: st.session_state.confirm_delete = False
    with tab1:
        c_search, c_filter = st.columns([2, 1])
        query = c_search.text_input("🔍 Quick Search...", placeholder="Type to search...")
        status_filter = c_filter.multiselect("Filter Status", ["Active", "Deactive"], default=["Active"])
        display_df = df[df['Status'].isin(status_filter)] if not df.empty else pd.DataFrame()
        if query and not display_df.empty: display_df = display_df[display_df['Name'].str.contains(query, case=False) | display_df['ID'].astype(str).str.contains(query)]
        st.markdown("""<div class="table-header"><div style="display: flex; justify-content: space-between;"><span style="flex: 0.5;">ID</span><span style="flex: 2;">Full Name</span><span style="flex: 1.5;">Designation</span><span style="flex: 1;">Type</span><span style="flex: 1;">Status</span><span style="flex: 1.2;">Joined</span><span style="flex: 1.2;">Salary</span><span style="flex: 0.8; text-align: right;">Action</span></div></div>""", unsafe_allow_html=True)
        if not display_df.empty:
            for _, row in display_df.iterrows():
                with st.container():
                    r_c1, r_c2, r_c3, r_c4, r_c5, r_c6, r_c7, r_c8 = st.columns([0.5, 2, 1.5, 1, 1, 1.2, 1.2, 0.8])
                    r_c1.write(f"#{int(row['ID'])}"); r_c2.write(f"**{row['Name']}**"); r_c3.write(f"{row['Role']}"); r_c4.write(f"{row.get('Employee Type', 'Full Time')}")
                    status_val = row['Status']; status_color = "#4ade80" if status_val == "Active" else "#f87171"
                    r_c5.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{status_val}</span>", unsafe_allow_html=True)
                    r_c6.write(f"{row['Joining Date']}"); r_c7.write(f"{row['Currency']} {row['Base Salary']:,.0f}")
                    if r_c8.button("✏️ Edit", key=f"btn_edit_{row['ID']}", use_container_width=True): st.session_state.edit_target_id = int(row['ID']); st.session_state.confirm_delete = False; st.rerun()
                    st.divider()
        if st.session_state.edit_target_id:
            st.markdown('<div id="edit-portal-section"></div>', unsafe_allow_html=True)
            components.html("""<script>window.parent.document.getElementById('edit-portal-section').scrollIntoView({behavior: 'smooth'});</script>""", height=0)
            st.markdown("---")
            ed = df[pd.to_numeric(df['ID'], errors='coerce') == st.session_state.edit_target_id].iloc[0]
            with st.container(border=True):
                e_c1, e_c2 = st.columns(2)
                up_name = e_c1.text_input("Full Name", value=ed['Name'])
                up_email = e_c2.text_input("Email (Username)", value=ed.get('Email', ''))
                e_c3, e_c4, e_c5 = st.columns(3)
                up_role = e_c3.selectbox("Designation", roles_list, index=roles_list.index(ed['Role']) if ed['Role'] in roles_list else 0)
                up_type = e_c4.selectbox("Employee Type", EMPLOYEE_TYPES, index=EMPLOYEE_TYPES.index(ed.get('Employee Type', 'Full Time')) if ed.get('Employee Type', 'Full Time') in EMPLOYEE_TYPES else 0)
                try: default_date = datetime.strptime(ed['Joining Date'], "%Y-%m-%d").date()
                except: default_date = datetime.now().date()
                up_date = e_c5.date_input("Joining Date", value=default_date)
                e_c6, e_c7, e_c8 = st.columns(3)
                up_sal = e_c6.number_input("Base Salary", value=float(ed['Base Salary']))
                up_curr = e_c7.selectbox("Currency", ["PKR", "USD"], index=0 if ed['Currency'] == "PKR" else 1)
                up_stat = e_c8.selectbox("Status", ["Active", "Deactive"], index=0 if ed['Status'] == "Active" else 1)
                if st.session_state.confirm_delete:
                    st.error(f"⚠️ Delete {ed['Name']} permanently?"); col_confirm, col_cancel_del = st.columns(2)
                    if col_confirm.button("✅ Yes, Delete Permanently", use_container_width=True): df = df[pd.to_numeric(df['ID'], errors='coerce') != st.session_state.edit_target_id]; save_data(df, EMPLOYEE_FILE); write_log(st.session_state.current_user, "Delete", f"deleted employee {ed['Name']}"); st.session_state.edit_target_id = None; st.session_state.confirm_delete = False; st.toast("Deleted.", icon="🗑️"); st.rerun()
                    if col_cancel_del.button("❌ No, Keep Employee", use_container_width=True): st.session_state.confirm_delete = False; st.rerun()
                else:
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_save, btn_cancel, btn_del = st.columns(3)
                    with btn_save:
                        if st.button("💾 Save Changes", use_container_width=True):
                            df.loc[pd.to_numeric(df['ID'], errors='coerce') == st.session_state.edit_target_id, ['Name', 'Role', 'Employee Type', 'Joining Date', 'Base Salary', 'Currency', 'Status', 'Email']] = [up_name, up_role, up_type, up_date.strftime("%Y-%m-%d"), up_sal, up_curr, up_stat, up_email]
                            save_data(df, EMPLOYEE_FILE); write_log(st.session_state.current_user, "Update", f"updated employee {up_name}"); st.session_state.edit_target_id = None; st.toast("Details updated!", icon="💾"); st.rerun()
                    with btn_cancel:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state.edit_target_id = None; st.rerun()
                    with btn_del:
                        if st.button("🗑️ Delete Employee", use_container_width=True):
                            st.session_state.confirm_delete = True; st.rerun()
    with tab2:
        with st.container(border=True):
            st.subheader("New Personnel Onboarding")
            f_col1, f_col2 = st.columns(2)
            with f_col1: new_name = st.text_input("Full Name", key="onboard_name"); new_email = st.text_input("Email (Username)", key="onboard_email")
            with f_col2: new_role = st.selectbox("Designation", roles_list, key="onboard_role"); new_type = st.selectbox("Employee Type", EMPLOYEE_TYPES, key="onboard_type")
            f_col3, f_col4, f_col5 = st.columns(3)
            with f_col3: new_date = st.date_input("Joining Date", datetime.now(), key="onboard_date")
            with f_col4: new_curr = st.selectbox("Currency", ["PKR", "USD"], key="onboard_curr")
            with f_col5: new_sal = st.number_input("Monthly Salary", min_value=0.0, step=1000.0, key="onboard_sal")
            btn_c1, btn_c2, btn_sp = st.columns([1.2, 1, 3])
            if btn_c1.button("➕ Add Employee", use_container_width=True):
                if not new_name or not new_email: st.error("Required fields missing.")
                else:
                    max_id = int(df["ID"].max() + 1) if not df.empty else 101
                    new_entry = pd.DataFrame([{"ID": max_id, "Name": new_name, "Role": new_role, "Employee Type": new_type, "Status": "Active", "Currency": new_curr, "Base Salary": new_sal, "Joining Date": new_date.strftime("%Y-%m-%d"), "Email": new_email.lower(), "Password": "123"}])
                    save_data(pd.concat([df, new_entry], ignore_index=True), EMPLOYEE_FILE); write_log(st.session_state.current_user, "Create", f"created employee {new_name}"); st.toast(f"Onboarded {new_name}!", icon='✅'); st.rerun()
            if btn_c2.button("🔄 Reset", use_container_width=True): st.rerun()

# ==========================================
# 5. PDF & PAYROLL LOGIC (PRESERVED)
# ==========================================
def generate_pdf(data, role, jd, rules):
    try:
        pdf = FPDF(); pdf.set_auto_page_break(auto=False); pdf.add_page(); pdf.set_margin(15); pdf.set_font("helvetica", "B", 18); pdf.cell(0, 10, "THE SOFTWARE DISTRICT", ln=True, align="C"); pdf.set_font("helvetica", "B", 12); pdf.cell(0, 8, f"SALARY SLIP - {str(data['Month'])}", ln=True, align="C"); pdf.line(15, 30, 195, 30); pdf.ln(5)
        pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(240, 240, 240); pdf.cell(0, 8, " EMPLOYEE INFORMATION", border=1, ln=True, fill=True); pdf.set_font("helvetica", "B", 9); pdf.set_fill_color(255, 255, 255); pdf.cell(40, 8, " Employee ID:", border="LTB"); pdf.set_font("helvetica", "", 9); pdf.cell(50, 8, f"#{int(float(data['Employee ID']))}", border="TB"); pdf.set_font("helvetica", "B", 9); pdf.cell(40, 8, " Full Name:", border="LTB"); pdf.set_font("helvetica", "", 9); pdf.cell(50, 8, str(data['Name']), border="TRB", ln=True)
        pdf.set_font("helvetica", "B", 9); pdf.cell(40, 8, " Joining Date:", border="LTB"); pdf.set_font("helvetica", "", 9); pdf.cell(50, 8, str(jd), border="TB"); pdf.set_font("helvetica", "B", 9); pdf.cell(40, 8, " Designation:", border="LTB"); pdf.set_font("helvetica", "", 9); pdf.cell(50, 8, str(role), border="TRB", ln=True); pdf.set_font("helvetica", "B", 9); pdf.cell(40, 8, " Monthly Base:", border="LTB"); pdf.set_font("helvetica", "", 9); pdf.cell(50, 8, f"{float(data['Base Salary']):,.0f}", border="TB"); pdf.set_font("helvetica", "B", 9); pdf.cell(40, 8, " Currency Unit:", border="LTB"); pdf.set_font("helvetica", "", 9); pdf.cell(50, 8, str(data['Currency']), border="TRB", ln=True); pdf.ln(10)
        pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(240, 240, 240); pdf.cell(130, 8, " EARNINGS COMPONENTS", border=1, fill=True); pdf.cell(50, 8, f" AMOUNT ({str(data['Currency'])})", border=1, fill=True, align="R"); pdf.ln(); pdf.set_font("helvetica", "", 9); pdf.cell(130, 8, " Monthly Standard Salary", border="LRB"); pdf.cell(50, 8, f"{float(data['Base Salary']):,.2f}", border="RB", align="R"); pdf.ln(); ctx = str(data['Bonus Context']) if pd.notna(data['Bonus Context']) and str(data['Bonus Context']).lower() != "nan" else "Regular"; pdf.cell(130, 8, f" Bonus / Incentives ({ctx})", border="LRB"); pdf.cell(50, 8, f"{float(data['Bonus']):,.2f}", border="RB", align="R"); pdf.ln(); pdf.ln(6); pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(240, 240, 240); pdf.cell(130, 8, " ATTENDANCE DEDUCTIONS", border=1, fill=True); pdf.cell(50, 8, " AMOUNT", border=1, fill=True, align="R"); pdf.ln(); daily_wage = float(data['Base Salary']) / 30; deductions = [("Lates", float(data['Lates']), "Late"), ("Extra Lates", float(data['Extra Lates']), "Extra Late"), ("Half Days", float(data['Half Days']), "Half Day"), ("Absents", float(data['Absents']), "Absent")]
        for label, days, key in deductions:
            x_start, y_start = pdf.get_x(), pdf.get_y(); pdf.rect(x_start, y_start, 130, 11); pdf.set_font("helvetica", "B", 9); pdf.set_xy(x_start + 2, y_start + 1.5); pdf.cell(120, 4, f"{label} ({int(days)} days)", ln=False); rate = float(rules[key]); pdf.set_font("helvetica", "I", 8); pdf.set_text_color(120, 120, 120); pdf.set_xy(x_start + 2, y_start + 5.5); pdf.cell(120, 3, f"{rate}% pay of the day", ln=False); pdf.set_font("helvetica", "", 9); pdf.set_text_color(0, 0, 0); pdf.set_xy(x_start + 130, y_start); amt = days * daily_wage * (rate / 100); pdf.cell(50, 11, f" - {amt:,.2f}", border=1, align="R"); pdf.set_xy(x_start, y_start + 11)
        pdf.ln(5); pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(15, 23, 42); pdf.set_text_color(255, 255, 255); pdf.cell(130, 12, " TOTAL NET PAYABLE", border=1, fill=True); pdf.cell(50, 12, f" {str(data['Currency'])} {float(data['Net Paid']):,.2f}", border=1, fill=True, align="R"); pdf.set_y(260); pdf.set_font("helvetica", "I", 8); pdf.set_text_color(150, 150, 150); pdf.cell(0, 4, "Generated by SD HRMS.", ln=True, align="C"); return bytes(pdf.output())
    except Exception as e: raise e

def open_pdf_js(pdf_bytes):
    b64 = base64.b64encode(pdf_bytes).decode()
    js = f"""<script>var pdfWindow = window.open(""); if (pdfWindow) {{ pdfWindow.document.write("<html><head><title>Slip</title></head><body style='margin:0;'><iframe width='100%' height='100%' src='data:application/pdf;base64,{b64}'></iframe></body></html>"); }}</script>"""
    components.html(js, height=0)

def show_payroll_management(emp_df):
    st.title("💳 Monthly Payroll")
    st.markdown("""<div class="section-desc"><strong>Salary Processing Center</strong><br>Default alphabetical sorting.</div>""", unsafe_allow_html=True)
    c_m, c_y = st.columns(2); month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]; month, year = c_m.selectbox("Month", month_names, index=datetime.now().month - 1), c_y.selectbox("Year", [2024, 2025, 2026], index=1); period = f"{month} {year}"; attendance_df, payroll_history = load_data(DAILY_ATTENDANCE_FILE), load_data(PAYROLL_FILE); active_emps = emp_df[emp_df['Status'] == 'Active'].copy().sort_values(by="Name")
    if active_emps.empty: st.warning("No active employees found."); return
    if st.button("🔄 Sync Attendance Records", use_container_width=True):
        m_idx = month_names.index(month) + 1
        if not attendance_df.empty:
            attendance_df['ParsedDate'] = pd.to_datetime(attendance_df['Date'], errors='coerce'); month_logs = attendance_df[(attendance_df['ParsedDate'].dt.year == year) & (attendance_df['ParsedDate'].dt.month == m_idx)]
            for _, row in active_emps.iterrows():
                eid_key = int(row['ID']); emp_logs = month_logs[month_logs['Employee ID'] == float(row['ID'])]; st.session_state[f"l_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Late"])); st.session_state[f"el_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Extra Late"])); st.session_state[f"hd_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Half Day"])); st.session_state[f"ab_{eid_key}"] = int(len(emp_logs[emp_logs['Status'] == "Absent"]))
            st.toast("Sync Complete", icon="🔄"); st.rerun()
    payroll_buffer = []
    with st.container(border=True):
        for _, row in active_emps.iterrows():
            eid_key = int(row['ID'])
            for k in ['l', 'el', 'hd', 'ab']:
                if f"{k}_{eid_key}" not in st.session_state: st.session_state[f"{k}_{eid_key}"] = 0
            c_head, c_btn = st.columns([4, 1.2]); c_head.markdown(f"#### {row['Name']}", unsafe_allow_html=True)
            hist_match = payroll_history[(payroll_history['Month'] == period) & (pd.to_numeric(payroll_history['Employee ID'], errors='coerce') == float(row['ID']))]
            if not hist_match.empty:
                if c_btn.button("📄 View Slip", key=f"view_{eid_key}", use_container_width=True): pdf_bytes = generate_pdf(hist_match.iloc[0], row['Role'], row['Joining Date'], get_attendance_rules()); open_pdf_js(pdf_bytes)
            p_cols = st.columns(4); l = p_cols[0].number_input("Late", min_value=0, key=f"l_{eid_key}"); el = p_cols[1].number_input("Extra Late", min_value=0, key=f"el_{eid_key}"); hd = p_cols[2].number_input("Half Day", min_value=0, key=f"hd_{eid_key}"); ab = p_cols[3].number_input("Absent", min_value=0, key=f"ab_{eid_key}"); b_cols = st.columns(2); bonus = b_cols[0].number_input("Bonus", min_value=0.0, key=f"bon_{eid_key}"); ctx = b_cols[1].text_input("Reason", key=f"ctx_{eid_key}")
            net, deduct = calculate_net_salary(row['Base Salary'], l, el, hd, ab, bonus); payroll_buffer.append({"Month": period, "Employee ID": row['ID'], "Name": row['Name'], "Base Salary": row['Base Salary'], "Currency": row['Currency'], "Lates": l, "Extra Lates": el, "Half Days": hd, "Absents": ab, "Deductions": deduct, "Bonus": bonus, "Bonus Context": ctx, "Net Paid": net}); st.divider()
    if st.button("🚀 Confirm & Process Payroll", use_container_width=True):
        if not payroll_history.empty: payroll_history = payroll_history[~((payroll_history['Month'] == period) & (payroll_history['Employee ID'].isin([float(p['Employee ID']) for p in payroll_buffer])))]
        save_data(pd.concat([payroll_history, pd.DataFrame(payroll_buffer)], ignore_index=True), PAYROLL_FILE); st.toast("Payroll archived", icon="🚀"); st.rerun()

def show_config():
    st.title("⚙️ Enterprise Configuration")
    t1, t2, t3 = st.tabs(["📋 Designation Management", "⚖️ Deduction Policy", "🕒 Time Windows"])
    with t1:
        roles_df = load_data(CONFIG_FILE); c1, c2 = st.columns([4, 1.2]); new_r = c1.text_input("New Role", label_visibility="collapsed")
        if c2.button("✨ Add Role"):
            if new_r: save_data(pd.concat([roles_df, pd.DataFrame({"Roles": [new_r]})], ignore_index=True), CONFIG_FILE); st.rerun()
        upd_roles = st.data_editor(roles_df, use_container_width=True, num_rows="dynamic", key="role_ed")
        if st.button("💾 Save Official Registry"): save_data(upd_roles, CONFIG_FILE); st.toast("Saved!", icon="💾")
    with t2:
        att_df = load_data(ATTENDANCE_CONFIG_FILE); upd = st.data_editor(att_df, use_container_width=True, column_config={"Parameter": st.column_config.TextColumn("Category", disabled=True), "Value": st.column_config.NumberColumn("% Deduction", format="%d%%")}, key="policy_ed")
        if st.button("💾 Apply Global Updates"): save_data(upd, ATTENDANCE_CONFIG_FILE); st.toast("Updated.", icon="⚖️")
    with t3:
        st.markdown("""<div class="section-desc"><strong>Attendance Timing Windows</strong><br>Define the hours for each status category. Format: HH:MM (24-hour). Anything outside these windows is 'Absent'.</div>""", unsafe_allow_html=True)
        time_df = load_data(TIME_POLICY_FILE); upd_time = st.data_editor(time_df, use_container_width=True, key="time_policy_ed")
        if st.button("💾 Save Time Windows"): save_data(upd_time, TIME_POLICY_FILE); st.toast("Time windows updated!", icon="🕒")

# ==========================================
# 7. MAIN ROUTING
# ==========================================
def main():
    init_storage()
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    
    if not st.session_state.authenticated: render_login_page()
    else:
        with st.sidebar:
            st.title("Side Menu")
            st.markdown(f"**User:** {st.session_state.current_user}")
            st.markdown(f"**Role:** {st.session_state.user_designation}")
            st.divider()
            
            if st.session_state.user_role == "Admin":
                nav_options = ["Dashboard", "Employee Records", "Daily Attendance", "Payroll Management", "Configuration", "Audit Logs"]
            else:
                nav_options = ["Dashboard", "Daily Attendance"]
            
            if "current_page" not in st.session_state: st.session_state.current_page = "Dashboard"

            for opt in nav_options:
                is_active = (st.session_state.current_page == opt)
                container_class = "active-nav" if is_active else "inactive-nav"
                st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
                icon = "🚀" if opt == "Dashboard" else "👥" if opt == "Employee Records" else "📅" if opt == "Daily Attendance" else "💳" if opt == "Payroll Management" else "⚙️" if opt == "Configuration" else "📜"
                if st.button(f"{icon} {opt}", use_container_width=True, key=f"nav_{opt}"):
                    st.session_state.current_page = opt
                    st.session_state.edit_target_id = None
                    st.session_state.confirm_delete = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("### User Settings")
            is_prof_active = (st.session_state.current_page == "Profile")
            st.markdown(f'<div class="{"active-nav" if is_prof_active else "inactive-nav"}">', unsafe_allow_html=True)
            if st.button("👤 Profile Settings", use_container_width=True):
                st.session_state.current_page = "Profile"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("🚪 Sign Out Session", use_container_width=True):
                st.session_state.authenticated = False; st.rerun()

        emp_df = load_data(EMPLOYEE_FILE)
        page = st.session_state.current_page
        
        if page == "Profile": show_profile_settings()
        elif page == "Dashboard": show_dashboard(emp_df)
        elif page == "Employee Records": show_employee_management(emp_df)
        elif page == "Daily Attendance": show_daily_attendance(emp_df)
        elif page == "Payroll Management": show_payroll_management(emp_df)
        elif page == "Configuration": show_config()
        elif page == "Audit Logs":
            st.title("📜 Audit Trail")
            c_clear, _ = st.columns([1, 4])
            if c_clear.button("🗑️ Delete All Logs", use_container_width=True): pd.DataFrame(columns=["Timestamp", "User", "Action", "Details"]).to_csv(LOG_FILE, index=False); st.rerun()
            logs = load_data(LOG_FILE)
            if not logs.empty:
                display_logs = logs.copy(); display_logs['Log Entry'] = display_logs.apply(lambda x: f"{x['User']} {x['Details']}", axis=1)
                st.dataframe(display_logs[['Timestamp', 'Log Entry']].iloc[::-1], use_container_width=True)
            else: st.info("No audit logs available.")

if __name__ == "__main__": main()