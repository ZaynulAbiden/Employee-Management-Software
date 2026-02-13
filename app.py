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

# Premium CSS for Enterprise Look
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    
    /* Dashboard & Config Cards */
    div.stVerticalBlock > div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background-color: white !important;
        padding: 25px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    /* Enterprise Panels */
    .enterprise-panel {
        background-color: #ffffff !important;
        border-left: 5px solid #0f172a;
        padding: 25px;
        border-radius: 4px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* Styled Green Add Button - Aligned and High Contrast */
    div[data-testid="stColumn"] button:contains("Add Role") {
        background-color: #22c55e !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        width: 100%;
        padding: 0.55rem !important;
        margin-top: 0px !important;
    }
    
    /* Tab Header Enhancement - Professional Typography */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #0f172a;
        letter-spacing: -0.02em;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom-color: #0f172a !important;
        background-color: #f8fafc !important;
    }

    .config-header {
        color: #0f172a;
        font-weight: 800;
        font-size: 1.6rem;
        margin-top: 15px;
        margin-bottom: 8px;
    }
    .config-desc {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 25px;
        line-height: 1.6;
        background: #f8fafc;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #0f172a;
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

    required_columns = ["ID", "Name", "Role", "Contact", "Status", "Currency", "Base Salary", "Joining Date"]
    
    if not os.path.exists(EMPLOYEE_FILE):
        df = pd.DataFrame([{
            "ID": 101, "Name": "Zayn Iftikhar", "Role": "CEO", 
            "Contact": "zayn@softwaredistrict.com", "Status": "Active",
            "Currency": "PKR", "Base Salary": 200000, "Joining Date": datetime.now().strftime("%Y-%m-%d")
        }])
        df.to_csv(EMPLOYEE_FILE, index=False)
    else:
        try:
            df = pd.read_csv(EMPLOYEE_FILE)
            changed = False
            defaults = {"Role": "Unity Developer", "Contact": "N/A", "Status": "Active", "Currency": "PKR", "Joining Date": datetime.now().strftime("%Y-%m-%d")}
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
        float(extra_lates) * (daily_wage * (rules["Extra Late"] / 100)) +
        float(half_days) * (daily_wage * (rules["Half Day"] / 100)) +
        float(absents) * (daily_wage * (rules["Absent"] / 100))
    )
    net = (float(base) + float(bonus)) - total_deductions
    return round(net, 2), round(total_deductions, 2)

# ==========================================
# 4. UI COMPONENTS
# ==========================================

def render_login_page():
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'><h1>The Software District</h1><p style='color: #64748b;'>HRMS Enterprise Portal</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            user_i = st.text_input("Username").lower()
            pass_i = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True, type="primary"):
                if user_i in USERS and USERS[user_i] == pass_i:
                    st.session_state.authenticated = True
                    st.session_state.current_user = user_i
                    write_log(user_i, "Login", "Successful Login")
                    st.rerun()
                else: st.error("Invalid credentials")

def show_dashboard(emp_df):
    st.title("🏢 Software District - HRMS Dashboard")
    t_count = len(emp_df) if not emp_df.empty else 0
    a_count = len(emp_df[emp_df['Status'] == 'Active']) if not emp_df.empty else 0
    d_count = len(emp_df[emp_df['Status'] == 'Deactive']) if not emp_df.empty else 0
    st.markdown(f"""
        <div class="enterprise-panel">
            <h3>Enterprise Overview</h3>
            <p>The Software District workforce management system is online. Personnel data synchronized.</p>
            <ul>
                <li><b>Total Workforce:</b> {t_count} Records</li>
                <li><b>Active Personnel:</b> {a_count} Employees</li>
                <li><b>Inactive Records:</b> {d_count} Files</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.subheader("Recent System Logs")
    logs = load_data(LOG_FILE)
    if not logs.empty: st.dataframe(logs.tail(10), use_container_width=True)

def show_daily_attendance(df):
    st.header("📅 Attendance Exception Portal")
    log_date = st.date_input("Log Date", datetime.now())
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

        if st.button("Save Daily Log", type="primary", use_container_width=True):
            if not attendance_df.empty: 
                attendance_df['Employee ID'] = pd.to_numeric(attendance_df['Employee ID'], errors='coerce')
                attendance_df = attendance_df[attendance_df['Date'] != date_str]
            attendance_df = pd.concat([attendance_df, pd.DataFrame(updated_attendance)], ignore_index=True)
            save_data(attendance_df, DAILY_ATTENDANCE_FILE)
            st.success(f"Log for {date_str} archived.")
            write_log(st.session_state.current_user, "Attendance", f"Updated {date_str}")

def show_employee_management(df):
    st.header("👥 Workforce Directory")
    roles_df = load_data(CONFIG_FILE)
    roles_list = roles_df["Roles"].tolist() if not roles_df.empty else ["Unity Developer"]
    tab1, tab2 = st.tabs(["Directory View", "Onboard Employee"])
    
    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    
    with tab1:
        search = st.text_input("Search Personnel...")
        display_df = df if not search else df[df['Name'].str.contains(search, case=False)]
        st.dataframe(display_df, use_container_width=True)
        sel_id = st.number_input("Input ID to Modify", min_value=0, step=1)
        if st.button("Open File"): st.session_state.edit_id = int(sel_id); st.rerun()
        
        if st.session_state.edit_id:
            emp = df[pd.to_numeric(df['ID'], errors='coerce') == st.session_state.edit_id]
            if not emp.empty:
                with st.container(border=True):
                    ed = emp.iloc[0]
                    st.subheader(f"Modify: {ed['Name']}")
                    m_name = st.text_input("Full Name", ed['Name'])
                    m_sal = st.number_input("Monthly Base Salary", value=float(ed['Base Salary']))
                    m_role = st.selectbox("Assign Role", roles_list, index=roles_list.index(ed['Role']) if ed['Role'] in roles_list else 0)
                    if st.button("Apply Changes"):
                        df.loc[pd.to_numeric(df['ID'], errors='coerce') == st.session_state.edit_id, ['Name', 'Base Salary', 'Role']] = [m_name, m_sal, m_role]
                        save_data(df, EMPLOYEE_FILE); st.session_state.edit_id = None; st.rerun()

    with tab2:
        with st.container(border=True):
            st.subheader("New Onboarding")
            new_name = st.text_input("Employee Full Name")
            new_sal = st.number_input("Starting Base Salary", min_value=0.0)
            new_role = st.selectbox("Designation", roles_list)
            if st.button("Onboard Personnel"):
                max_id = int(df["ID"].max() + 1) if not df.empty else 101
                new_row = pd.DataFrame([{"ID": max_id, "Name": new_name, "Role": new_role, "Status": "Active", "Currency": "PKR", "Base Salary": new_sal, "Joining Date": datetime.now().strftime("%Y-%m-%d"), "Contact": "N/A"}])
                save_data(pd.concat([df, new_row], ignore_index=True), EMPLOYEE_FILE); st.rerun()

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
        pdf.cell(130, 8, " Monthly Base Salary", border="LRB")
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
        pdf.cell(0, 4, "Official Payment Proof - Generated Automatically.", ln=True, align="C")
        pdf.cell(0, 4, "Strictly Confidential - The Software District HRMS.", ln=True, align="C")
        
        return bytes(pdf.output())
    except Exception as e:
        raise e

def open_pdf_js(pdf_bytes):
    b64 = base64.b64encode(pdf_bytes).decode()
    js = f"""<script>var pdfWindow = window.open(""); if (pdfWindow) {{ pdfWindow.document.write("<html><head><title>Salary Slip</title></head><body style='margin:0; padding:0;'><iframe width='100%' height='100%' style='border:none;' src='data:application/pdf;base64,{b64}'></iframe></body></html>"); }} else {{ alert("Popup blocked!"); }}</script>"""
    components.html(js, height=0)

def show_payroll_management(emp_df):
    st.header("💳 Monthly Payroll Processing")
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
            st.toast(f"Attendance Synced for {period}"); st.rerun()

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
            bonus = b_cols[0].number_input("Incentive", min_value=0.0, key=f"bon_{eid_key}")
            ctx = b_cols[1].text_input("Reason", placeholder="Reward context...", key=f"ctx_{eid_key}")
            
            net, deduct = calculate_net_salary(row['Base Salary'], l, el, hd, ab, bonus)
            payroll_buffer.append({"Month": period, "Employee ID": row['ID'], "Name": row['Name'], "Base Salary": row['Base Salary'], "Currency": row['Currency'], "Lates": l, "Extra Lates": el, "Half Days": hd, "Absents": ab, "Deductions": deduct, "Bonus": bonus, "Bonus Context": ctx, "Net Paid": net})
            st.divider()

    if st.button("🚀 Process & Generate Payroll", type="primary", use_container_width=True):
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
    t1, t2 = st.tabs(["📋 Designation Registry", "⚖️ Deduction Policy"])
    
    with t1:
        st.markdown('<p class="config-header">Job Title Registry</p>', unsafe_allow_html=True)
        st.markdown('<p class="config-desc">Define professional roles within Software District. These designations appear as selection options during onboarding.</p>', unsafe_allow_html=True)
        roles_df = load_data(CONFIG_FILE)
        c1, c2 = st.columns([4, 1.2])
        new_r = c1.text_input("New Designation Title", placeholder="Enter job title...", label_visibility="collapsed")
        if c2.button("Add Role"):
            if new_r: save_data(pd.concat([roles_df, pd.DataFrame({"Roles": [new_r]})], ignore_index=True), CONFIG_FILE); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        upd_roles = st.data_editor(roles_df, use_container_width=True, num_rows="dynamic", key="role_ed")
        if st.button("Save Registry"): save_data(upd_roles, CONFIG_FILE); st.rerun()

    with t2:
        st.markdown('<p class="config-header">Deduction Rate Policy</p>', unsafe_allow_html=True)
        st.markdown('<p class="config-desc">Impact of attendance exceptions. Penalties are % of daily wage (Monthly Base / 30).</p>', unsafe_allow_html=True)
        att_df = load_data(ATTENDANCE_CONFIG_FILE)
        upd = st.data_editor(att_df, use_container_width=True, column_config={"Parameter": st.column_config.TextColumn("Category", disabled=True), "Value": st.column_config.NumberColumn("% of Deduction", format="%d%%")}, key="policy_ed")
        if st.button("Apply Updates"): save_data(upd, ATTENDANCE_CONFIG_FILE); st.rerun()

def main():
    init_storage()
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if not st.session_state.authenticated: render_login_page()
    else:
        with st.sidebar:
            st.title("SD - HRMS"); st.markdown(f"**Admin:** {st.session_state.current_user}"); st.divider()
            page = st.radio("Navigation", ["Dashboard", "Workforce Directory", "Daily Attendance", "Payroll Management", "Configuration", "System Logs"])
            if st.button("Sign Out Session", use_container_width=True): st.session_state.authenticated = False; st.rerun()
        emp_df = load_data(EMPLOYEE_FILE)
        if page == "Dashboard": show_dashboard(emp_df)
        elif page == "Workforce Directory": show_employee_management(emp_df)
        elif page == "Daily Attendance": show_daily_attendance(emp_df)
        elif page == "Payroll Management": show_payroll_management(emp_df)
        elif page == "Configuration": show_config()
        elif page == "System Logs":
            st.title("📜 Audit Trail"); logs = load_data(LOG_FILE)
            if not logs.empty: st.dataframe(logs.iloc[::-1], use_container_width=True)

if __name__ == "__main__": main()