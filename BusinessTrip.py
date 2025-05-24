import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import traceback # For detailed error logging

# 1. İLK STREAMLIT ƏMRİ OLMALIDIR!
st.set_page_config(
    page_title="Ezamiyyət İdarəetmə Sistemi",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Logging Function ---
def write_log(action, details="", user="system"):
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "details": details,
        }
        log_file = "admin_logs.json"
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except json.JSONDecodeError: # Handle corrupted log file
                logs = []
        logs.append(log_entry)
        if len(logs) > 1000: # Keep last 1000 logs
            logs = logs[-1000:]
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Log yazma xətası: {e}") # Print to console if st.error is not appropriate here

# 2. GİRİŞ MƏNTİQİ
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Giriş üçün CSS
st.markdown("""
<style>
    .login-box {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
        max-width: 500px;
        margin: 5rem auto;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput input {
        background-color: rgba(255,255,255,0.2)!important;
        color: white!important;
        border: 1px solid rgba(255,255,255,0.3)!important;
        border-radius: 8px!important;
        padding: 8px 12px!important;
        font-size: 14px!important;
    }
    .stTextInput input::placeholder {
        color: rgba(255,255,255,0.7)!important;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    with st.container():
        st.markdown('<div class="login-box"><div class="login-header"><h2>🔐 Sistemə Giriş</h2></div>', unsafe_allow_html=True)
        
        access_code = st.text_input("Giriş kodu", type="password", 
                                  label_visibility="collapsed", 
                                  placeholder="Giriş kodunu daxil edin...",
                                  key="main_login_password")
        
        cols_login_main = st.columns([1,2,1])
        with cols_login_main[1]:
            if st.button("Daxil ol", use_container_width=True, key="main_login_button"):
                if access_code == "admin": # CHANGE THIS FOR PRODUCTION
                    st.session_state.logged_in = True
                    write_log("Sistemə giriş", user="istifadəçi")
                    st.rerun()
                else:
                    st.error("Yanlış giriş kodu!")
                    write_log("Sistemə giriş cəhdi", "Yanlış kod", user="naməlum")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 3. ƏSAS TƏRTİBAT VƏ PROQRAM MƏNTİQİ
st.markdown("""
<style>
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --background-color: #ffffff;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 0 0 20px 20px;
    }
    
    .section-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white!important;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: none;
    }
    
    /* Main buttons - keep as is */
    .stButton>button {
        border-radius: 8px!important;
        padding: 0.5rem 1.5rem!important;
        transition: all 0.3s ease!important;
        border: 1px solid var(--primary-color)!important;
        background: var(--secondary-color)!important;
        color: white!important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(99,102,241,0.3)!important;
        background: var(--primary-color)!important;
    }
    
    /* Destructive buttons */
    .stButton button[kind="destructive"] {
        background-color: #ef4444 !important; /* Tailwind red-500 */
        border-color: #dc2626 !important; /* Tailwind red-600 */
    }
    .stButton button[kind="destructive"]:hover {
        background-color: #dc2626 !important;
        border-color: #b91c1c !important; /* Tailwind red-700 */
    }
    
    .dataframe {
        border-radius: 12px!important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05)!important;
    }
</style>
""", unsafe_allow_html=True)

# ============================== SABİTLƏR ==============================
DEPARTMENTS = [
    "Statistika işlərinin əlaqələndirilməsi və strateji planlaşdırma şöbəsi", "Keyfiyyətin idarə edilməsi və metaməlumatlar şöbəsi",
    "Milli hesablar və makroiqtisadi göstəricilər statistikası şöbəsi", "Kənd təsərrüfatı statistikası şöbəsi",
    "Sənaye və tikinti statistikası şöbəsi", "Energetika və ətraf mühit statistikası şöbəsi", "Ticarət statistikası şöbəsi",
    "Sosial statistika şöbəsi", "Xidmət statistikası şöbəsi", "Əmək statistikası şöbəsi", "Qiymət statistikası şöbəsi",
    "Əhali statistikası şöbəsi", "Həyat keyfiyyətinin statistikası şöbəsi", "Dayanıqlı inkişaf statistikası şöbəsi",
    "İnformasiya texnologiyaları şöbəsi", "İnformasiya və ictimaiyyətlə əlaqələr şöbəsi", "Beynəlxalq əlaqələr şöbəsi",
    "İnsan resursları və hüquq şöbəsi", "Maliyyə və təsərrüfat şöbəsi", "Ümumi şöbə", "Rejim və məxfi kargüzarlıq şöbəsi",
    "Elmi - Tədqiqat və Statistik İnnovasiyalar Mərkəzi", "Yerli statistika orqanları", "Digər"
]

CITIES = [
    "Abşeron", "Ağcabədi", "Ağdam", "Ağdaş", "Ağdərə", "Ağstafa", "Ağsu", "Astara", "Bakı", "Babək (Naxçıvan MR)", "Balakən", "Bərdə",
    "Beyləqan", "Biləsuvar", "Cəbrayıl", "Cəlilabad", "Culfa (Naxçıvan MR)", "Daşkəsən", "Füzuli", "Gədəbəy", "Gəncə", "Goranboy",
    "Göyçay", "Göygöl", "Hacıqabul", "Xaçmaz", "Xankəndi", "Xızı", "Xocalı", "Xocavənd", "İmişli", "İsmayıllı", "Kəlbəcər",
    "Kəngərli (Naxçıvan MR)", "Kürdəmir", "Laçın", "Lənkəran", "Lerik", "Masallı", "Mingəçevir", "Naftalan", "Neftçala", "Naxçıvan",
    "Oğuz", "Siyəzən", "Ordubad (Naxçıvan MR)", "Qəbələ", "Qax", "Qazax", "Qobustan", "Quba", "Qubadlı", "Qusar", "Saatlı", "Sabirabad",
    "Sədərək (Naxçıvan MR)", "Salyan", "Samux", "Şabran", "Şahbuz (Naxçıvan MR)", "Şamaxı", "Şəki", "Şəmkir", "Şərur (Naxçıvan MR)",
    "Şirvan", "Şuşa", "Sumqayıt", "Tərtər", "Tovuz", "Ucar", "Yardımlı", "Yevlax", "Zaqatala", "Zəngilan", "Zərdab", "Nabran", "Xudat"
]

COUNTRIES = {
    "Türkiyə": 300, "Gürcüstan": 250, "Almaniya": 600, "BƏƏ": 500, "Rusiya": 400, "İran": 280, "İtaliya": 550, "Fransa": 580,
    "İngiltərə": 620, "ABŞ": 650, "Qazaxıstan": 350, "Özbəkistan": 320, "Ukrayna": 380, "Belarus": 360, "Digər": 450
}

DOMESTIC_ROUTES = {
    ("Bakı", "Ağcabədi"): 10.50, ("Bakı", "Ağdam"): 13.50, ("Bakı", "Ağdaş"): 10.30, ("Bakı", "Astara"): 10.40, ("Bakı", "Şuşa"): 28.90,
    ("Bakı", "Balakən"): 17.30, ("Bakı", "Beyləqan"): 10.00, ("Bakı", "Bərdə"): 11.60, ("Bakı", "Biləsuvar"): 6.50, ("Bakı", "Cəlilabad"): 7.10,
    ("Bakı", "Füzuli"): 10.80, ("Bakı", "Gədəbəy"): 16.50, ("Bakı", "Gəncə"): 13.10, ("Bakı", "Goranboy"): 9.40, ("Bakı", "Göyçay"): 9.20,
    ("Bakı", "Göygöl"): 13.50, ("Bakı", "İmişli"): 8.10, ("Bakı", "İsmayıllı"): 7.00, ("Bakı", "Kürdəmir"): 7.10, ("Bakı", "Lənkəran"): 8.80,
    ("Bakı", "Masallı"): 7.90, ("Bakı", "Mingəçevir"): 11.40, ("Bakı", "Naftalan"): 12.20, ("Bakı", "Oğuz"): 13.10, ("Bakı", "Qax"): 14.60,
    ("Bakı", "Qazax"): 17.60, ("Bakı", "Qəbələ"): 11.50, ("Bakı", "Quba"): 5.90, ("Bakı", "Qusar"): 6.40, ("Bakı", "Saatlı"): 7.10,
    ("Bakı", "Sabirabad"): 6.10, ("Bakı", "Şəki"): 13.20, ("Bakı", "Şəmkir"): 15.00, ("Bakı", "Siyəzən"): 3.60, ("Bakı", "Tərtər"): 12.20,
    ("Bakı", "Tovuz"): 16.40, ("Bakı", "Ucar"): 8.90, ("Bakı", "Xaçmaz"): 5.50, ("Bakı", "Nabran"): 7.20, ("Bakı", "Xudat"): 6.30,
    ("Bakı", "Zaqatala"): 15.60, ("Bakı", "Zərdab"): 9.30
}
DOMESTIC_DEFAULT_PRICE = 7.00 # Default price if route not in DOMESTIC_ROUTES

PAYMENT_TYPES = {
    "Ödənişsiz": 0,
    "10% ödəniş edilməklə": 0.1,
    "Tam ödəniş edilməklə": 1
}

# ============================== FUNKSİYALAR ==============================
@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_trip_data():
    """Ezamiyyət məlumatlarını yükləyir"""
    try:
        if os.path.exists("ezamiyyet_melumatlari.xlsx"):
            df = pd.read_excel(
                "ezamiyyet_melumatlari.xlsx",
                parse_dates=['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            )
            date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Məlumat yükləmə xətası: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache config for 1 hour
def load_system_config():
    try:
        if os.path.exists("system_config.json"):
            with open("system_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def calculate_domestic_amount(from_city, to_city):
    return DOMESTIC_ROUTES.get((from_city, to_city), DOMESTIC_DEFAULT_PRICE)

def calculate_days(start_date, end_date):
    if isinstance(start_date, datetime): start_date = start_date.date()
    if isinstance(end_date, datetime): end_date = end_date.date()
    return (end_date - start_date).days + 1

def calculate_total_amount(daily_allowance, days, payment_type, ticket_price=0):
    return (daily_allowance * days + ticket_price) * PAYMENT_TYPES.get(payment_type, 1) # Default to full payment if type unknown

def save_trip_data(data_dict):
    try:
        df_new = pd.DataFrame([data_dict])
        df_existing = load_trip_data() # Use the cached function
        
        # Ensure new data columns match existing or are handled
        if not df_existing.empty:
            # Align columns - important if new_df has different columns
            for col in df_existing.columns:
                if col not in df_new.columns:
                    df_new[col] = pd.NA # Or appropriate default
            for col in df_new.columns:
                if col not in df_existing.columns:
                    df_existing[col] = pd.NA


            df_combined = pd.concat([df_existing, df_new[df_existing.columns]], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
        st.cache_data.clear() # Clear cache for load_trip_data
        return True
    except Exception as e:
        st.error(f"Yadda saxlama xətası: {str(e)}")
        return False

# --- Initialize session state for confirmations ---
if "show_duplicate_deletion_confirmation" not in st.session_state:
    st.session_state.show_duplicate_deletion_confirmation = False
if "confirm_delete_all_prompt" not in st.session_state:
    st.session_state.confirm_delete_all_prompt = False
if "confirm_reset_system_prompt" not in st.session_state:
    st.session_state.confirm_reset_system_prompt = False

# ============================== ƏSAS İNTERFEYS ==============================
st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli"])

# ============================== YENİ EZAMİYYƏT HISSESI ==============================
with tab1:
    with st.container():
        col1_form, col2_form = st.columns([2, 1], gap="large")
        
        with col1_form: # Sol Sütun - Məlumat Girişi
            with st.form(key="new_trip_form"):
                with st.expander("👤 Şəxsi Məlumatlar", expanded=True):
                    f_cols = st.columns(2)
                    first_name = f_cols[0].text_input("Ad*", key="fn")
                    father_name = f_cols[0].text_input("Ata adı", key="fan")
                    last_name = f_cols[1].text_input("Soyad*", key="ln")
                    position = f_cols[1].text_input("Vəzifə*", key="pos")

                with st.expander("🏢 Təşkilat Məlumatları"):
                    department = st.selectbox("Şöbə*", DEPARTMENTS, key="dept")

                with st.expander("🧳 Ezamiyyət Detalları"):
                    trip_type = st.radio("Növ*", ["Ölkə daxili", "Ölkə xarici"], key="tt", horizontal=True)
                    payment_type = st.selectbox("Ödəniş növü*", list(PAYMENT_TYPES.keys()), key="pt")
                    
                    ticket_price_form = 0.0
                    daily_allowance_form = 0.0
                    accommodation_form = "Tətbiq edilmir"
                    from_city_form = "Bakı"
                    to_city_form = ""

                    if trip_type == "Ölkə daxili":
                        loc_cols = st.columns(2)
                        from_city_form = loc_cols[0].selectbox("Haradan*", CITIES, index=CITIES.index("Bakı") if "Bakı" in CITIES else 0, key="fc_dom")
                        available_to_cities = [c for c in CITIES if c != from_city_form] if CITIES else []
                        if not available_to_cities and CITIES : available_to_cities = [CITIES[0]] if CITIES[0]!= from_city_form else ([CITIES[1]] if len(CITIES)>1 else ["Digər"])

                        to_city_form = loc_cols[1].selectbox("Haraya*", available_to_cities if available_to_cities else ["Şəhər seçin"], key="tc_dom")
                        
                        ticket_price_form = calculate_domestic_amount(from_city_form, to_city_form)
                        daily_allowance_form = 70.0 # Default for domestic
                    else: # Ölkə xarici
                        country_form = st.selectbox("Ölkə*", list(COUNTRIES.keys()), key="country_int")
                        payment_mode_form = st.selectbox("Ödəniş rejimi", ["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"], key="pm_int")
                        accommodation_form = st.selectbox("Qonaqlama xərcləri", ["Adi rejim", "Yalnız yaşayış yeri ilə təmin edir", "Yalnız gündəlik xərcləri təmin edir"], key="acc_int")
                        
                        base_allowance_form = COUNTRIES.get(country_form, 0)
                        if payment_mode_form == "Günlük Normaya 50% əlavə": daily_allowance_form = base_allowance_form * 1.5
                        elif payment_mode_form == "Günlük Normaya 30% əlavə": daily_allowance_form = base_allowance_form * 1.3
                        else: daily_allowance_form = base_allowance_form
                        
                        from_city_form = "Bakı"
                        to_city_form = country_form
                        # Ticket price for international is often handled separately or set to 0 here.
                        ticket_price_form = st.number_input("Beynəlxalq Bilet Qiyməti (AZN, əgər varsa)", min_value=0.0, value=0.0, step=10.0, key="tp_int")


                    date_cols = st.columns(2)
                    start_date_form = date_cols[0].date_input("Başlanğıc tarixi*", value=datetime.today(), key="sd")
                    end_date_form = date_cols[1].date_input("Bitmə tarixi*", value=datetime.today() + timedelta(days=1), min_value=start_date_form, key="ed")
                    
                    purpose_form = st.text_area("Ezamiyyət məqsədi*", key="purp")
                
                submitted_form = st.form_submit_button("✅ Yadda Saxla", use_container_width=True)

        with col2_form: # Sağ Sütun - Hesablama
            with st.container(border=True): # Use border for visual separation
                st.markdown('<div class="section-header" style="margin-top:0;">💰 Hesablama</div>', unsafe_allow_html=True)
                
                trip_days_form = 0
                total_amount_form = 0.0
                delta_label_form = None

                if start_date_form and end_date_form:
                    if end_date_form >= start_date_form:
                        trip_days_form = calculate_days(start_date_form, end_date_form)
                        total_amount_form = calculate_total_amount(daily_allowance_form, trip_days_form, payment_type, ticket_price_form)

                        if trip_type == "Ölkə xarici":
                            if accommodation_form == "Yalnız yaşayış yeri ilə təmin edir":
                                total_amount_form *= 1.4 
                                delta_label_form = "40% artım (Yaşayış)"
                            elif accommodation_form == "Yalnız gündəlik xərcləri təmin edir":
                                total_amount_form *= 1.6
                                delta_label_form = "60% artım (Gündəlik)"
                        
                        st.metric("📅 Günlük müavinət", f"{daily_allowance_form:.2f} AZN")
                        if trip_type == "Ölkə daxili" or (trip_type == "Ölkə xarici" and ticket_price_form > 0):
                            st.metric("✈️/🚌 Nəqliyyat xərci", f"{ticket_price_form:.2f} AZN")
                        st.metric("⏳ Müddət", f"{trip_days_form} gün")
                        st.metric(
                            "💳 Ümumi məbləğ", f"{total_amount_form:.2f} AZN",
                            delta=delta_label_form,
                            delta_color="normal" if delta_label_form else "off"
                        )
                    else:
                        st.error("Bitmə tarixi başlanğıc tarixindən əvvəl ola bilməz.")
                else:
                    st.info("Hesablama üçün tarixləri daxil edin.")
        
        if submitted_form:
            # Validation
            required_fields = {
                "Ad": first_name, "Soyad": last_name, "Vəzifə": position, 
                "Şöbə": department, "Haraya": to_city_form, "Ezamiyyət məqsədi": purpose_form
            }
            missing = [name for name, val in required_fields.items() if not val]

            if missing:
                st.error(f"Zəhmət olmasa bütün məcburi sahələri ({', '.join(missing)}) doldurun!")
            elif end_date_form < start_date_form:
                 st.error("Bitmə tarixi başlanğıc tarixindən əvvəl ola bilməz.")
            else:
                trip_data_to_save = {
                    "Tarix": pd.Timestamp(datetime.now()), "Ad": first_name, "Soyad": last_name, "Ata adı": father_name,
                    "Vəzifə": position, "Şöbə": department, "Ezamiyyət növü": trip_type, "Ödəniş növü": payment_type,
                    "Qonaqlama növü": accommodation_form, "Marşrut": f"{from_city_form} → {to_city_form}",
                    "Bilet qiyməti": ticket_price_form, "Günlük müavinət": daily_allowance_form,
                    "Başlanğıc tarixi": pd.Timestamp(start_date_form), "Bitmə tarixi": pd.Timestamp(end_date_form),
                    "Günlər": trip_days_form, "Ümumi məbləğ": total_amount_form, "Məqsəd": purpose_form
                }
                if save_trip_data(trip_data_to_save):
                    st.success("Məlumatlar yadda saxlandı!")
                    write_log("Yeni ezamiyyət", f"İşçi: {first_name} {last_name}, Məbləğ: {total_amount_form:.2f}", user="istifadəçi")
                    st.balloons()
                # else: save_trip_data shows its own error

# ============================== ADMIN PANELİ ==============================
with tab2:
    if 'admin_logged' not in st.session_state: st.session_state.admin_logged = False
    if 'admin_session_time' not in st.session_state: st.session_state.admin_session_time = datetime.now()

    if st.session_state.admin_logged:
        if datetime.now() - st.session_state.admin_session_time > timedelta(minutes=30): # 30 min session
            st.session_state.admin_logged = False
            write_log("Admin sessiyası", "Sessiya müddəti bitdi", user="admin")
            st.warning("Sessiya müddəti bitdi. Yenidən giriş edin.")
            st.rerun()

    if not st.session_state.admin_logged:
        st.markdown("""<div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:3rem; border-radius:20px; box-shadow:0 20px 40px rgba(0,0,0,0.1); margin:2rem auto; max-width:500px; text-align:center;"><h2 style="color:white; margin-bottom:2rem;">🔐 Admin Panel Giriş</h2></div>""", unsafe_allow_html=True)
        login_cols = st.columns([1,2,1])
        with login_cols[1]:
            with st.form("admin_login_form_panel"):
                admin_user = st.text_input("👤 İstifadəçi adı", placeholder="admin", key="admin_user_login_panel")
                admin_pass = st.text_input("🔒 Şifrə", type="password", placeholder="••••••••", key="admin_pass_login_panel")
                if st.form_submit_button("🚀 Giriş Et", use_container_width=True):
                    if admin_user == "admin" and admin_pass == "admin123": # CHANGE FOR PRODUCTION
                        st.session_state.admin_logged = True
                        st.session_state.admin_session_time = datetime.now()
                        write_log("Admin panel girişi", user="admin")
                        st.success("✅ Uğurlu giriş!")
                        st.rerun()
                    else:
                        write_log("Admin panel giriş cəhdi", f"Yanlış məlumatlar: user='{admin_user}'", user="naməlum")
                        st.error("❌ Yanlış giriş məlumatları!")
        st.stop()

    if st.session_state.admin_logged:
        st.markdown("""<div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:2rem; border-radius:15px; margin-bottom:2rem; box-shadow:0 10px 30px rgba(0,0,0,0.1);"><h1 style="color:white; text-align:center; margin:0;">⚙️ Admin İdarəetmə Paneli</h1><p style="color:rgba(255,255,255,0.8); text-align:center; margin:0.5rem 0 0 0;">Ezamiyyət sisteminin tam idarəetməsi</p></div>""", unsafe_allow_html=True)
        
        head_cols = st.columns([2,1,1])
        head_cols[0].info(f"👋 Xoş gəlmisiniz, Admin! Sessiya başlama: {st.session_state.admin_session_time.strftime('%d.%m.%Y %H:%M')}")
        if head_cols[1].button("🔄 Sessiya Yenilə", key="refresh_session_admin"):
            st.session_state.admin_session_time = datetime.now()
            st.success("Sessiya yeniləndi!")
            write_log("Admin sessiyası yeniləndi", user="admin")
        if head_cols[2].button("🚪 Çıxış Et", type="secondary", key="logout_admin"): # Changed to secondary for less emphasis
            st.session_state.admin_logged = False
            write_log("Admin panel çıxışı", user="admin")
            st.rerun()

        admin_tab_names = ["📊 Dashboard", "🗂️ Məlumat İdarəetməsi", "📈 Analitika", "📥 İdxal/İxrac", "⚙️ Sistem Parametrləri", "👥 İstifadəçi Aktivliyi", "🔧 Sistem Alətləri"]
        admin_tabs_obj = st.tabs(admin_tab_names)

        # 1. DASHBOARD TAB
        with admin_tabs_obj[0]:
            st.markdown("### "+ admin_tab_names[0])
            try:
                df_dashboard = load_trip_data()
                if not df_dashboard.empty:
                    # Data prep (ensure columns exist and are correct type)
                    date_cols_dash = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                    for col in date_cols_dash:
                        if col in df_dashboard.columns: df_dashboard[col] = pd.to_datetime(df_dashboard[col], errors='coerce')
                    
                    num_cols_dash = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti', 'Günlər']
                    for col in num_cols_dash:
                        if col in df_dashboard.columns: df_dashboard[col] = pd.to_numeric(df_dashboard[col], errors='coerce').fillna(0)

                    # Metrics
                    m_cols = st.columns(5)
                    total_trips = len(df_dashboard)
                    recent_trips_count = 0
                    if 'Tarix' in df_dashboard.columns and not df_dashboard['Tarix'].isnull().all():
                        recent_trips_count = (df_dashboard['Tarix'] >= (pd.Timestamp.now() - timedelta(days=30))).sum()
                    m_cols[0].metric("📋 Ümumi Ezamiyyət", total_trips, delta=f"+{recent_trips_count} son 30 gün" if recent_trips_count > 0 else None)
                    
                    total_expense = df_dashboard['Ümumi məbləğ'].sum() if 'Ümumi məbləğ' in df_dashboard.columns else 0
                    avg_expense = (total_expense / total_trips) if total_trips > 0 else 0
                    m_cols[1].metric("💰 Ümumi Xərclər", f"{total_expense:,.2f} AZN", delta=f"{avg_expense:,.2f} AZN orta" if avg_expense > 0 else None)
                    
                    avg_duration = df_dashboard['Günlər'].mean() if 'Günlər' in df_dashboard.columns and df_dashboard['Günlər'].notna().any() else 0
                    m_cols[2].metric("⏱️ Orta Müddət", f"{avg_duration:.1f} gün" if avg_duration > 0 else "N/A")

                    active_users = 0
                    if 'Ad' in df_dashboard.columns and 'Soyad' in df_dashboard.columns:
                        active_users = df_dashboard.groupby(['Ad', 'Soyad']).ngroups
                    elif 'Ad' in df_dashboard.columns:
                        active_users = df_dashboard['Ad'].nunique()
                    m_cols[3].metric("👥 Aktiv İstifadəçilər", active_users)

                    international_pct = 0.0
                    if 'Ezamiyyət növü' in df_dashboard.columns and total_trips > 0:
                        international_pct = (df_dashboard['Ezamiyyət növü'] == 'Ölkə xarici').sum() / total_trips * 100
                    m_cols[4].metric("🌍 Beynəlxalq %", f"{international_pct:.1f}%")

                    # Son Ezamiyyətlər
                    st.markdown("#### 📅 Son Ezamiyyətlər (Top 5)")
                    df_recent_display = df_dashboard.copy()
                    if 'Tarix' in df_recent_display.columns: df_recent_display = df_recent_display.sort_values('Tarix', ascending=False)
                    
                    for _, row in df_recent_display.head(5).iterrows():
                        r_cols = st.columns([2,2,1,1])
                        r_cols[0].write(f"**{row.get('Ad','N/A')} {row.get('Soyad','N/A')}**")
                        r_cols[0].caption(str(row.get('Şöbə','N/A'))[:30]+"...")
                        r_cols[1].write(f"📍 {row.get('Marşrut','N/A')}")
                        r_cols[1].caption(f"🗓️ {pd.to_datetime(row.get('Başlanğıc tarixi')).strftime('%d.%m.%Y') if pd.notna(row.get('Başlanğıc tarixi')) else 'N/A'}")
                        r_cols[2].write(f"💰 {row.get('Ümumi məbləğ',0):.2f} AZN")
                        odenis_status = row.get('Ödəniş növü', 'N/A')
                        status_color = "🟢" if "Tam" in odenis_status else ("🟡" if "10%" in odenis_status else "🔴")
                        r_cols[3].write(f"{status_color} {odenis_status}")
                        st.divider()

                    # Charts
                    chart_cols = st.columns(2)
                    if 'Ezamiyyət növü' in df_dashboard.columns and df_dashboard['Ezamiyyət növü'].notna().any():
                        trip_type_counts = df_dashboard['Ezamiyyət növü'].value_counts()
                        if not trip_type_counts.empty:
                            fig_pie = px.pie(trip_type_counts, values=trip_type_counts.values, names=trip_type_counts.index, title='🌍 Ezamiyyət Növləri', hole=0.4)
                            chart_cols[0].plotly_chart(fig_pie, use_container_width=True)
                    
                    if 'Ödəniş növü' in df_dashboard.columns and df_dashboard['Ödəniş növü'].notna().any():
                        payment_type_counts = df_dashboard['Ödəniş növü'].value_counts()
                        if not payment_type_counts.empty:
                            fig_bar = px.bar(payment_type_counts, x=payment_type_counts.index, y=payment_type_counts.values, title='💳 Ödəniş Növləri', labels={'x':'Ödəniş Növü', 'y':'Sayı'}, color=payment_type_counts.values, color_continuous_scale='Blues')
                            chart_cols[1].plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.warning("📭 Hələ heç bir ezamiyyət qeydiyyatı yoxdur.")
            except Exception as e:
                st.error(f"❌ Dashboard yüklənərkən xəta: {e}")
                st.code(traceback.format_exc())

        # 2. MƏLUMAT İDARƏETMƏSİ TAB
        with admin_tabs_obj[1]:
            st.markdown("### "+ admin_tab_names[1])
            try:
                df_manage = load_trip_data()
                if not df_manage.empty:
                    df_editable = df_manage.copy() # Work with a copy for edits
                    for col in ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']:
                        if col in df_editable.columns: df_editable[col] = pd.to_datetime(df_editable[col], errors='coerce')

                    # Dublikat Təhlili
                    st.markdown("#### 🔍 Dublikat Təhlili")
                    dup_cols_default = [c for c in ['Ad', 'Soyad', 'Başlanğıc tarixi', 'Marşrut'] if c in df_editable.columns]
                    if not dup_cols_default and len(df_editable.columns) > 0: dup_cols_default = df_editable.columns.tolist()[:min(4, len(df_editable.columns))]
                    
                    duplicate_columns_selected = st.multiselect("Dublikat axtarışı üçün sütunlar", df_editable.columns.tolist(), default=dup_cols_default, key="dup_cols_select_manage")

                    if duplicate_columns_selected:
                        duplicates_mask = df_editable.duplicated(subset=duplicate_columns_selected, keep=False)
                        duplicates_df_view = df_editable[duplicates_mask]
                        
                        if not duplicates_df_view.empty:
                            st.warning(f"⚠️ {duplicates_df_view.duplicated(subset=duplicate_columns_selected, keep='first').sum()} qrupda {len(duplicates_df_view)} potensial dublikat qeyd tapıldı!")
                            with st.expander("Dublikat Qeydlər (klikləyin)", expanded=False):
                                st.dataframe(duplicates_df_view, use_container_width=True)
                            
                            dup_strat_cols = st.columns(2)
                            dup_strategy = dup_strat_cols[0].selectbox("Dublikat silmə strategiyası", ["İlk qeydi saxla", "Son qeydi saxla", "Ən yüksək 'Ümumi məbləğ' olanı saxla", "Ən aşağı 'Ümumi məbləğ' olanı saxla"], key="dup_strategy_select")
                            if dup_strat_cols[1].button("🧹 Seçilmiş Strategiya ilə Dublikatları Təmizlə", key="clean_dup_btn_manage"):
                                cleaned_df_temp = df_editable.copy()
                                if "İlk" in dup_strategy: cleaned_df_temp = cleaned_df_temp.drop_duplicates(subset=duplicate_columns_selected, keep='first')
                                elif "Son" in dup_strategy: cleaned_df_temp = cleaned_df_temp.drop_duplicates(subset=duplicate_columns_selected, keep='last')
                                elif "'Ümumi məbləğ'" in dup_strategy and 'Ümumi məbləğ' in cleaned_df_temp.columns:
                                    cleaned_df_temp['Ümumi məbləğ'] = pd.to_numeric(cleaned_df_temp['Ümumi məbləğ'], errors='coerce')
                                    keep_option = 'last' if "yüksək" in dup_strategy else 'first'
                                    cleaned_df_temp = cleaned_df_temp.sort_values('Ümumi məbləğ', ascending=("yüksək" not in dup_strategy))
                                    cleaned_df_temp = cleaned_df_temp.drop_duplicates(subset=duplicate_columns_selected, keep=keep_option)
                                else:
                                    st.error("'Ümumi məbləğ' sütunu tələb olunur və ya strategiya uyğun deyil.")
                                
                                removed_count = len(df_editable) - len(cleaned_df_temp)
                                if removed_count > 0:
                                    st.session_state.df_to_clean_duplicates = cleaned_df_temp
                                    st.session_state.removed_duplicates_count = removed_count
                                    st.session_state.show_duplicate_deletion_confirmation = True
                                    st.rerun()
                                else:
                                    st.info("Silinəcək dublikat tapılmadı (seçilmiş strategiyaya görə).")
                        else:
                            st.success("✅ Seçilmiş sütunlara görə dublikat qeyd tapılmadı.")
                    
                    # Confirmation Dialog for Duplicate Deletion (if triggered)
                    if st.session_state.get("show_duplicate_deletion_confirmation", False):
                        st.error(f"⚠️ {st.session_state.removed_duplicates_count} dublikat qeydin silinməsi planlaşdırılır. Davam etmək istəyirsiniz?")
                        confirm_cols = st.columns(2)
                        if confirm_cols[0].button("Bəli, Dublikatları Sil", type="destructive", key="confirm_delete_duplicates_final_btn"):
                            try:
                                df_to_save_cleaned = st.session_state.df_to_clean_duplicates
                                df_to_save_cleaned.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                st.success(f"✅ {st.session_state.removed_duplicates_count} qeyd silindi! Səhifə yenilənir...")
                                write_log("Məlumat təmizləmə", f"{st.session_state.removed_duplicates_count} dublikat silindi", user="admin")
                                st.cache_data.clear()
                                # Clean up session state
                                for key in ["show_duplicate_deletion_confirmation", "df_to_clean_duplicates", "removed_duplicates_count"]:
                                    if key in st.session_state: del st.session_state[key]
                                st.rerun()
                            except Exception as e_clean_save:
                                st.error(f"Dublikatları silmə zamanı xəta: {e_clean_save}")
                        if confirm_cols[1].button("Xeyr, Ləğv Et", key="cancel_delete_duplicates_final_btn"):
                            for key in ["show_duplicate_deletion_confirmation", "df_to_clean_duplicates", "removed_duplicates_count"]:
                                if key in st.session_state: del st.session_state[key]
                            st.info("Dublikat silmə əməliyyatı ləğv edildi.")
                            st.rerun()
                        st.stop() # Stop further execution until confirmation is handled


                    # Filtr və Axtarış
                    st.markdown("#### 🔍 Filtr və Axtarış")
                    filter_cols = st.columns(3)
                    df_filtered_manage = df_editable.copy()

                    date_filter = filter_cols[0].selectbox("📅 Tarix filtri ('Tarix' sütununa görə)", ["Hamısı", "Son 7 gün", "Son 30 gün", "Son 3 ay", "Bu il", "Seçilmiş aralıq"], key="date_f_mng")
                    if date_filter != "Hamısı" and 'Tarix' in df_filtered_manage.columns and not df_filtered_manage['Tarix'].isnull().all():
                        now = pd.Timestamp.now()
                        if date_filter == "Son 7 gün": df_filtered_manage = df_filtered_manage[df_filtered_manage['Tarix'] >= (now - timedelta(days=7))]
                        elif date_filter == "Son 30 gün": df_filtered_manage = df_filtered_manage[df_filtered_manage['Tarix'] >= (now - timedelta(days=30))]
                        elif date_filter == "Son 3 ay": df_filtered_manage = df_filtered_manage[df_filtered_manage['Tarix'] >= (now - timedelta(days=90))]
                        elif date_filter == "Bu il": df_filtered_manage = df_filtered_manage[df_filtered_manage['Tarix'].dt.year == now.year]
                        elif date_filter == "Seçilmiş aralıq":
                            sf_cols = st.columns(2)
                            start_f = sf_cols[0].date_input("Başlanğıc", datetime.today() - timedelta(days=30), key="sf_mng")
                            end_f = sf_cols[1].date_input("Bitmə", datetime.today(), key="ef_mng", min_value=start_f)
                            df_filtered_manage = df_filtered_manage[(df_filtered_manage['Tarix'].dt.date >= start_f) & (df_filtered_manage['Tarix'].dt.date <= end_f)]
                    
                    dept_options = ["Hamısı"] + (df_editable['Şöbə'].dropna().unique().tolist() if 'Şöbə' in df_editable.columns else [])
                    dept_filter = filter_cols[1].selectbox("🏢 Şöbə", dept_options, key="dept_f_mng")
                    if dept_filter != "Hamısı": df_filtered_manage = df_filtered_manage[df_filtered_manage['Şöbə'] == dept_filter]

                    type_options = ["Hamısı"] + (df_editable['Ezamiyyət növü'].dropna().unique().tolist() if 'Ezamiyyət növü' in df_editable.columns else [])
                    type_filter = filter_cols[2].selectbox("✈️ Növ", type_options, key="type_f_mng")
                    if type_filter != "Hamısı": df_filtered_manage = df_filtered_manage[df_filtered_manage['Ezamiyyət növü'] == type_filter]
                    
                    search_term = st.text_input("🔎 Ad/Soyad/Marşrut/Məqsəd axtarışı", key="search_t_mng")
                    if search_term:
                        search_cols_list = [c for c in ['Ad', 'Soyad', 'Marşrut', 'Məqsəd'] if c in df_filtered_manage.columns]
                        if search_cols_list:
                             df_filtered_manage = df_filtered_manage[df_filtered_manage[search_cols_list].astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)]
                    
                    st.markdown(f"#### 📊 Nəticələr ({len(df_filtered_manage)} qeyd)")
                    if not df_filtered_manage.empty:
                        cols_to_display_default = [c for c in ['Ad', 'Soyad', 'Şöbə', 'Marşrut', 'Ümumi məbləğ', 'Başlanğıc tarixi'] if c in df_filtered_manage.columns]
                        cols_to_display = st.multiselect("Göstəriləcək sütunlar", df_filtered_manage.columns.tolist(), default=cols_to_display_default, key="disp_c_mng")
                        
                        if cols_to_display:
                            # For editing, we need to ensure indices align with the original df_editable
                            # Pass the filtered DataFrame's relevant columns to data_editor
                            edited_df_from_editor = st.data_editor(
                                df_filtered_manage[cols_to_display],
                                column_config={
                                    "Tarix": st.column_config.DateColumn("Tarix", format="DD.MM.YYYY"),
                                    "Başlanğıc tarixi": st.column_config.DateColumn("Baş. tarixi", format="DD.MM.YYYY"),
                                    "Bitmə tarixi": st.column_config.DateColumn("Bit. tarixi", format="DD.MM.YYYY"),
                                    "Ümumi məbləğ": st.column_config.NumberColumn("Məbləğ", format="%.2f AZN")
                                },
                                use_container_width=True, height=400, key="editor_mng", num_rows="dynamic"
                            )
                            if st.button("💾 Data Editordan Dəyişiklikləri Saxla", key="save_editor_mng"):
                                try:
                                    # This updates df_editable (the full data copy) where indices match
                                    # It handles value changes in the displayed filtered set.
                                    # Deletions from data_editor are harder to map back perfectly without complex index tracking.
                                    # A simple approach: assume editor only modifies/deletes from the *filtered view*.
                                    # We can update the original df_editable based on the indices from df_filtered_manage.
                                    
                                    # Create a temporary df with original indices of edited rows
                                    temp_edited_df = edited_df_from_editor.copy()
                                    temp_edited_df.index = df_filtered_manage.index[edited_df_from_editor.index] # Map editor's default index to original index

                                    df_editable.update(temp_edited_df)
                                    
                                    # For rows deleted in editor (num_rows="dynamic"):
                                    # Identify original indices that were in df_filtered_manage but not in temp_edited_df.index
                                    original_filtered_indices = set(df_filtered_manage.index)
                                    edited_view_indices = set(temp_edited_df.index)
                                    indices_to_delete_from_editable = list(original_filtered_indices - edited_view_indices)

                                    if indices_to_delete_from_editable:
                                        df_editable.drop(index=indices_to_delete_from_editable, inplace=True)

                                    df_editable.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                    st.success("✅ Məlumatlar data editordan yeniləndi!")
                                    write_log("Məlumat redaktəsi (Data Editor)", f"{len(edited_df_from_editor)} sətir təsirləndi", user="admin")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e_save_editor:
                                    st.error(f"❌ Data editor dəyişikliklərini saxlama xətası: {e_save_editor}")
                        
                        # Kütləvi əməliyyatlar (filtrlənmiş df_filtered_manage üzərində)
                        st.markdown("#### ⚡ Kütləvi Əməliyyatlar (Filtrlənmiş məlumatlar üzərində)")
                        bulk_cols = st.columns(2)
                        if bulk_cols[0].button("📤 CSV İxrac (Filtrlənmiş)", key="csv_exp_f_mng"):
                            csv_f = df_filtered_manage[cols_to_display if cols_to_display else df_filtered_manage.columns].to_csv(index=False).encode('utf-8')
                            st.download_button("⬇️ Yüklə", data=csv_f, file_name="ezamiyyetler_filtred.csv", mime="text/csv")
                        
                        indices_for_selection = df_filtered_manage.index.tolist()
                        selected_indices_to_delete = bulk_cols[1].multiselect("Silmək üçün seçin (Filtrlənmiş siyahıdan)", indices_for_selection, format_func=lambda x: f"ID {x}: {df_filtered_manage.loc[x,'Ad'] if 'Ad' in df_filtered_manage else ''} {df_filtered_manage.loc[x,'Soyad'] if 'Soyad' in df_filtered_manage else ''}", key="sel_del_mng")
                        if selected_indices_to_delete:
                            if st.button("🗑️ Seçilmişləri Sil", type="destructive", key="del_sel_mng_btn"): # Use destructive for delete
                                if st.checkbox("Silməni təsdiq edirəm", key="confirm_del_sel_mng"):
                                    df_editable.drop(index=selected_indices_to_delete, inplace=True)
                                    df_editable.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                    st.success(f"✅ {len(selected_indices_to_delete)} qeyd silindi!")
                                    write_log("Kütləvi silmə", f"{len(selected_indices_to_delete)} qeyd silindi", user="admin")
                                    st.cache_data.clear()
                                    st.rerun()
                    else:
                        st.info("🔍 Filtrlərə uyğun nəticə tapılmadı.")
                else:
                    st.warning("📭 Hələ heç bir məlumat yoxdur.")
            except Exception as e:
                st.error(f"❌ Məlumat idarəetməsi tabında kritik xəta: {e}")
                st.code(traceback.format_exc())


        # 3. ANALİTİKA TAB
        with admin_tabs_obj[2]:
            st.markdown("### "+ admin_tab_names[2])
            try:
                df_analytics = load_trip_data()
                if not df_analytics.empty:
                    df_an = df_analytics.copy() # Work on a copy
                    for col in ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']:
                        if col in df_an.columns: df_an[col] = pd.to_datetime(df_an[col], errors='coerce')
                    for col in ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti', 'Günlər']:
                        if col in df_an.columns: df_an[col] = pd.to_numeric(df_an[col], errors='coerce').fillna(0)

                    if 'Tarix' in df_an.columns and not df_an['Tarix'].isnull().all():
                        df_an['Ay'] = df_an['Tarix'].dt.to_period('M')
                        df_an['İl'] = df_an['Tarix'].dt.year
                        try:
                            df_an['Həftənin günü'] = df_an['Tarix'].dt.day_name(locale='az_AZ.UTF-8')
                        except LocaleError: # Fallback if locale not found
                            df_an['Həftənin günü'] = df_an['Tarix'].dt.day_name()


                    analysis_type = st.selectbox("📊 Analiz növü", ["Zaman Analizi", "Şöbə Analizi", "Coğrafi Analiz", "Maliyyə Analizi", "Məqsəd Analizi"], key="an_type")

                    if analysis_type == "Zaman Analizi" and 'Ay' in df_an.columns:
                        st.markdown("#### 📅 Zamansal Trendlər")
                        an_cols1 = st.columns(2)
                        monthly_stats = df_an.groupby('Ay').agg(total_expense=('Ümumi məbləğ', 'sum'), trip_count=('Ad', 'count')).reset_index()
                        monthly_stats['Ay'] = monthly_stats['Ay'].astype(str)
                        if not monthly_stats.empty:
                            fig_t = make_subplots(specs=[[{"secondary_y": True}]])
                            fig_t.add_trace(go.Bar(x=monthly_stats['Ay'], y=monthly_stats['total_expense'], name="Xərclər (AZN)"), secondary_y=False)
                            fig_t.add_trace(go.Scatter(x=monthly_stats['Ay'], y=monthly_stats['trip_count'], name="Ezamiyyət sayı", mode="lines+markers"), secondary_y=True)
                            fig_t.update_layout(title_text="Aylıq Ezamiyyət Trendləri")
                            an_cols1[0].plotly_chart(fig_t, use_container_width=True)
                        
                        if 'Həftənin günü' in df_an.columns:
                            weekday_order = ["Bazar ertəsi", "Çərşənbə axşamı", "Çərşənbə", "Cümə axşamı", "Cümə", "Şənbə", "Bazar"]
                            weekday_stats = df_an['Həftənin günü'].value_counts().reindex(weekday_order).fillna(0)
                            if not weekday_stats.empty:
                                fig_w = px.bar(weekday_stats, x=weekday_stats.index, y=weekday_stats.values, title="Həftəlik Ezamiyyət Paylanması", labels={'index':'Gün', 'y':'Sayı'})
                                an_cols1[1].plotly_chart(fig_w, use_container_width=True)
                    
                    elif analysis_type == "Şöbə Analizi" and 'Şöbə' in df_an.columns:
                        st.markdown("#### 🏢 Şöbə əsaslı Analiz")
                        dept_agg_spec = {'Ümumi məbləğ': ['sum', 'mean', 'count']}
                        if 'Günlər' in df_an.columns: dept_agg_spec['Günlər'] = 'mean'
                        dept_stats = df_an.groupby('Şöbə').agg(dept_agg_spec).round(2)
                        col_names = ['Ümumi Xərc', 'Orta Xərc', 'Ezamiyyət Sayı']
                        if 'Günlər' in df_an.columns: col_names.append('Orta Müddət')
                        dept_stats.columns = col_names
                        dept_stats = dept_stats.sort_values('Ümumi Xərc', ascending=False)
                        
                        an_cols2 = st.columns(2)
                        if not dept_stats.empty:
                            fig_d_bar = px.bar(dept_stats.head(10), y=dept_stats.head(10).index, x='Ümumi Xərc', orientation='h', title="Top 10 Xərc Edən Şöbə")
                            an_cols2[0].plotly_chart(fig_d_bar, use_container_width=True)
                            
                            if 'Ezamiyyət Sayı' in dept_stats.columns and (dept_stats['Ezamiyyət Sayı']>0).any():
                                dept_stats['Xərc/Ezamiyyət'] = (dept_stats['Ümumi Xərc'] / dept_stats['Ezamiyyət Sayı']).fillna(0)
                                fig_d_scatter = px.scatter(dept_stats[dept_stats['Ezamiyyət Sayı']>0].head(15), x='Ezamiyyət Sayı', y='Orta Xərc', size='Ümumi Xərc', color='Xərc/Ezamiyyət', hover_name=dept_stats[dept_stats['Ezamiyyət Sayı']>0].head(15).index, title="Şöbə Effektivliyi")
                                an_cols2[1].plotly_chart(fig_d_scatter, use_container_width=True)
                        st.markdown("##### Detallı Şöbə Statistikaları")
                        st.dataframe(dept_stats.style.format({'Ümumi Xərc':'{:.2f} AZN', 'Orta Xərc':'{:.2f} AZN', 'Orta Müddət':'{:.1f} gün', 'Xərc/Ezamiyyət':'{:.2f} AZN/ezam.'}), use_container_width=True)

                    elif analysis_type == "Coğrafi Analiz" and 'Marşrut' in df_an.columns:
                        st.markdown("#### 🌍 Coğrafi Paylanma")
                        an_cols3 = st.columns(2)
                        route_counts = df_an['Marşrut'].value_counts().head(15)
                        if not route_counts.empty:
                            fig_r = px.bar(route_counts, y=route_counts.index, x=route_counts.values, orientation='h', title="Top 15 Marşrut")
                            an_cols3[0].plotly_chart(fig_r, use_container_width=True)
                        
                        if 'Ezamiyyət növü' in df_an.columns and 'Ümumi məbləğ' in df_an.columns:
                            geo_sum = df_an.groupby(['Ezamiyyət növü', 'Marşrut'])['Ümumi məbləğ'].sum().reset_index()
                            if not geo_sum[geo_sum['Ümumi məbləğ']>0].empty:
                                fig_tree = px.treemap(geo_sum[geo_sum['Ümumi məbləğ']>0], path=['Ezamiyyət növü', 'Marşrut'], values='Ümumi məbləğ', title="Coğrafi Xərc Paylanması")
                                an_cols3[1].plotly_chart(fig_tree, use_container_width=True)

                    # ... (Maliyyə və Məqsəd Analizi could be similarly detailed if needed for "active")
                    elif analysis_type == "Maliyyə Analizi" and 'Ümumi məbləğ' in df_an.columns:
                        st.markdown("#### 💰 Maliyyə Performansı")
                        # Add some basic financial plots or tables here
                        st.metric("Ümumi Xərclənən Məbləğ", f"{df_an['Ümumi məbləğ'].sum():,.2f} AZN")
                        st.metric("Ezamiyyət Başına Orta Xərc", f"{df_an['Ümumi məbləğ'].mean():,.2f} AZN")
                        if 'Ödəniş növü' in df_an.columns:
                             payment_expense_dist = df_an.groupby('Ödəniş növü')['Ümumi məbləğ'].sum()
                             if not payment_expense_dist.empty:
                                 fig_fin_pie = px.pie(payment_expense_dist, values=payment_expense_dist.values, names=payment_expense_dist.index, title="Xərclərin Ödəniş Növünə Görə Payı")
                                 st.plotly_chart(fig_fin_pie, use_container_width=True)


                    elif analysis_type == "Məqsəd Analizi" and 'Məqsəd' in df_an.columns:
                        st.markdown("#### 🎯 Ezamiyyət Məqsədləri")
                        purpose_counts = df_an['Məqsəd'].value_counts().head(10)
                        if not purpose_counts.empty:
                            fig_purp = px.bar(purpose_counts, x=purpose_counts.index, y=purpose_counts.values, title="Top 10 Ezamiyyət Məqsədi (Sayına görə)")
                            st.plotly_chart(fig_purp, use_container_width=True)


                    st.markdown("#### 📄 Hesabat İxracı")
                    exp_cols = st.columns(3)
                    if exp_cols[0].button("📊 Excel Hesabatı Yarat (Analitika)", key="excel_an_exp"):
                        buffer_an = BytesIO()
                        with pd.ExcelWriter(buffer_an, engine='openpyxl') as writer:
                            df_an.to_excel(writer, sheet_name='Əsas Məlumatlar', index=False)
                            # Add more sheets based on selected analysis if needed
                        st.download_button(label="⬇️ Excel Hesabatını Yüklə", data=buffer_an.getvalue(), file_name="analitik_hesabat.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    exp_cols[1].button("📈 PDF Hesabatı (Gələcəkdə)", disabled=True, key="pdf_an_exp")
                    exp_cols[2].button("📧 Email Göndər (Gələcəkdə)", disabled=True, key="email_an_exp")
                else:
                    st.warning("📊 Analiz üçün məlumat yoxdur.")
            except Exception as e:
                st.error(f"❌ Analitika tabında kritik xəta: {e}")
                st.code(traceback.format_exc())

        # 4. İDXAL/İXRAC TAB
        with admin_tabs_obj[3]:
            st.markdown("### "+ admin_tab_names[3])
            io_cols = st.columns(2)
            with io_cols[0]: # İxrac
                st.markdown("#### 📤 İxrac Seçimləri")
                df_io_exp = load_trip_data()
                if not df_io_exp.empty:
                    exp_format = st.selectbox("Fayl formatı", ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"], key="exp_fmt_io")
                    
                    exp_date_cols = st.columns(2)
                    min_dt = df_io_exp['Tarix'].min().date() if 'Tarix' in df_io_exp.columns and not df_io_exp['Tarix'].isnull().all() else datetime.today().date() - timedelta(days=30)
                    max_dt = df_io_exp['Tarix'].max().date() if 'Tarix' in df_io_exp.columns and not df_io_exp['Tarix'].isnull().all() else datetime.today().date()
                    start_dt_exp = exp_date_cols[0].date_input("Başlanğıc tarixi (ixrac)", min_dt, key="sd_exp_io")
                    end_dt_exp = exp_date_cols[1].date_input("Bitmə tarixi (ixrac)", max_dt, min_value=start_dt_exp, key="ed_exp_io")

                    all_cols_exp = df_io_exp.columns.tolist()
                    sel_cols_exp = st.multiselect("İxrac ediləcək sütunlar", all_cols_exp, default=all_cols_exp, key="sel_c_exp_io")

                    if st.button("📤 İxrac Et", type="primary", key="exp_btn_io"):
                        if not sel_cols_exp:
                            st.warning("İxrac üçün sütun seçin.")
                        else:
                            df_to_export = df_io_exp.copy()
                            if 'Tarix' in df_to_export.columns:
                                df_to_export = df_to_export[(df_to_export['Tarix'].dt.date >= start_dt_exp) & (df_to_export['Tarix'].dt.date <= end_dt_exp)]
                            df_final_export = df_to_export[sel_cols_exp]

                            if df_final_export.empty:
                                st.info("Seçilmiş filterlərə uyğun ixrac üçün məlumat yoxdur.")
                            else:
                                fname = f"ezamiyyet_ixrac_{datetime.now().strftime('%Y%m%d_%H%M')}"
                                if "Excel" in exp_format:
                                    buffer = BytesIO()
                                    df_final_export.to_excel(buffer, index=False, engine='openpyxl')
                                    st.download_button("⬇️ Excel Yüklə", buffer.getvalue(), f"{fname}.xlsx", "application/vnd.ms-excel")
                                elif "CSV" in exp_format:
                                    csv = df_final_export.to_csv(index=False).encode('utf-8')
                                    st.download_button("⬇️ CSV Yüklə", csv, f"{fname}.csv", "text/csv")
                                elif "JSON" in exp_format:
                                    js = df_final_export.to_json(orient='records', indent=2, date_format='iso')
                                    st.download_button("⬇️ JSON Yüklə", js.encode('utf-8'), f"{fname}.json", "application/json")
                                write_log("Məlumat ixracı", f"{len(df_final_export)} qeyd, Format: {exp_format}", user="admin")
                else:
                    st.info("İxrac üçün məlumat yoxdur.")

            with io_cols[1]: # İdxal
                st.markdown("#### 📥 İdxal Seçimləri")
                uploaded_file = st.file_uploader("Fayl seçin (.xlsx, .csv, .json)", type=['xlsx', 'csv', 'json'], key="uploader_io")
                if uploaded_file:
                    try:
                        ext = uploaded_file.name.split('.')[-1].lower()
                        df_new_imp = pd.DataFrame()
                        if ext == 'xlsx': df_new_imp = pd.read_excel(uploaded_file)
                        elif ext == 'csv': df_new_imp = pd.read_csv(uploaded_file)
                        elif ext == 'json': df_new_imp = pd.read_json(uploaded_file) # May need orient='records' etc.
                        
                        # Basic date parsing for common columns
                        for col_date in ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']:
                            if col_date in df_new_imp.columns:
                                df_new_imp[col_date] = pd.to_datetime(df_new_imp[col_date], errors='coerce')


                        if not df_new_imp.empty:
                            st.markdown("##### İdxal Əvvəli Nəzər (ilk 5 sətir)")
                            st.dataframe(df_new_imp.head(), height=200)
                            st.info(f"Faylda {len(df_new_imp)} qeyd, {len(df_new_imp.columns)} sütun tapıldı.")

                            import_mode = st.radio("İdxal rejimi", ["Əlavə et", "Əvəzlə", "Birləşdir (dublikatları yoxla)"], key="imp_mode_io", horizontal=True)
                            
                            pk_cols_imp = []
                            if import_mode == "Birləşdir (dublikatları yoxla)":
                                df_existing_cols = load_trip_data().columns.tolist()
                                common_cols_for_pk = [c for c in df_new_imp.columns if c in df_existing_cols]
                                default_pk = [c for c in ['Ad', 'Soyad', 'Başlanğıc tarixi'] if c in common_cols_for_pk]
                                pk_cols_imp = st.multiselect("Birləşdirmə üçün açar sütunlar (dublikat yoxlanışı üçün)", common_cols_for_pk, default=default_pk, key="pk_imp_io")


                            if st.button("📥 İdxal Et", type="primary", key="imp_btn_io_confirm"):
                                if import_mode == "Birləşdir (dublikatları yoxla)" and not pk_cols_imp:
                                    st.error("Birləşdirmə üçün açar sütun seçilməlidir.")
                                else:
                                    df_existing_io = load_trip_data()
                                    df_final_imp = pd.DataFrame()

                                    if import_mode == "Əlavə et":
                                        df_final_imp = pd.concat([df_existing_io, df_new_imp], ignore_index=True)
                                    elif import_mode == "Əvəzlə":
                                        df_final_imp = df_new_imp
                                    elif import_mode == "Birləşdir (dublikatları yoxla)":
                                        # Ensure consistent dtypes for merge keys if possible
                                        for col_pk in pk_cols_imp:
                                            if col_pk in df_existing_io.columns and col_pk in df_new_imp.columns:
                                                try: # Attempt to make types consistent, e.g., for dates or numbers stored as objects
                                                    if pd.api.types.is_datetime64_any_dtype(df_existing_io[col_pk]) or pd.api.types.is_datetime64_any_dtype(df_new_imp[col_pk]):
                                                        df_existing_io[col_pk] = pd.to_datetime(df_existing_io[col_pk], errors='coerce')
                                                        df_new_imp[col_pk] = pd.to_datetime(df_new_imp[col_pk], errors='coerce')
                                                except Exception: pass # Ignore conversion errors for now

                                        df_combined_merge = pd.concat([df_existing_io, df_new_imp], ignore_index=True)
                                        df_final_imp = df_combined_merge.drop_duplicates(subset=pk_cols_imp, keep='last') # Keep the one from the new file in case of duplicate
                                    
                                    df_final_imp.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                    st.success(f"✅ Məlumatlar idxal edildi ({len(df_new_imp)} sətir emal edildi, Nəticədə {len(df_final_imp)} sətir).")
                                    write_log("Məlumat idxalı", f"Rejim: {import_mode}, {len(df_new_imp)} sətir yükləndi", user="admin")
                                    st.cache_data.clear()
                                    st.rerun()
                        else:
                            st.warning("Yüklənən fayl boşdur və ya məlumat oxuna bilmədi.")
                    except Exception as e_imp:
                        st.error(f"Fayl oxuma və ya idxal xətası: {e_imp}")
                        st.code(traceback.format_exc())


        # 5. SİSTEM PARAMETRLƏRİ TAB
        with admin_tabs_obj[4]:
            st.markdown("### "+ admin_tab_names[4])
            config = load_system_config()
            
            set_cols1, set_cols2 = st.columns(2)
            with set_cols1:
                st.markdown("#### 🎨 İnterfeys (Gələcəkdə tətbiq üçün)")
                theme = st.selectbox("Tema rəngi", ["Mavi", "Yaşıl", "Qırmızı"], index=["Mavi", "Yaşıl", "Qırmızı"].index(config.get("theme_color", "Mavi")), key="th_set")
                lang = st.selectbox("Sistem dili", ["Azərbaycan", "English"], index=["Azərbaycan", "English"].index(config.get("language", "Azərbaycan")), key="lang_set")
            with set_cols2:
                st.markdown("#### 📊 Məlumat (Gələcəkdə tətbiq üçün)")
                rec_page = st.number_input("Səhifə başına qeyd", 10, 100, config.get("records_per_page", 20), 5, key="rec_set")
                auto_bck = st.checkbox("Avtomatik backup", config.get("auto_backup", True), key="ab_set", help="Bu funksiya serverdə xüsusi quraşdırma tələb edə bilər.")
            
            if st.button("💾 Parametrləri Saxla", type="primary", key="save_cfg_btn"):
                new_cfg = {
                    "theme_color": theme, "language": lang, "records_per_page": rec_page, "auto_backup": auto_bck,
                    "last_updated": datetime.now().isoformat()
                }
                with open("system_config.json", "w", encoding="utf-8") as f:
                    json.dump(new_cfg, f, indent=2, ensure_ascii=False)
                st.success("✅ Sistem parametrləri saxlanıldı!")
                write_log("Sistem parametrləri yeniləndi", user="admin")
                st.cache_data.clear() # Clear config cache


        # 6. İSTİFADƏÇİ İDARƏETMƏSİ TAB
        with admin_tabs_obj[5]:
            st.markdown("### "+ admin_tab_names[5])
            df_users_view = load_trip_data()
            if not df_users_view.empty and 'Ad' in df_users_view.columns and 'Soyad' in df_users_view.columns:
                user_agg_spec_view = {'Ümumi məbləğ': ['sum', 'count', 'mean']}
                if 'Tarix' in df_users_view.columns: user_agg_spec_view['Tarix'] = 'max'
                
                user_stats_view = df_users_view.groupby(['Ad', 'Soyad']).agg(user_agg_spec_view).round(2)
                user_cols = ['Cəmi Xərc', 'Ezamiyyət Sayı', 'Orta Xərc']
                if 'Tarix' in df_users_view.columns: user_cols.append('Son Ezamiyyət')
                user_stats_view.columns = user_cols
                user_stats_view = user_stats_view.sort_values('Cəmi Xərc', ascending=False)

                user_v_cols = st.columns([3,2])
                with user_v_cols[0]:
                    st.markdown("#### 📊 İstifadəçi Statistikaları")
                    style_user = {'Cəmi Xərc':'{:.2f} AZN', 'Orta Xərc':'{:.2f} AZN'}
                    if 'Son Ezamiyyət' in user_stats_view.columns:
                        user_stats_view['Son Ezamiyyət'] = pd.to_datetime(user_stats_view['Son Ezamiyyət'])
                        style_user['Son Ezamiyyət'] = lambda x: x.strftime('%d.%m.%Y') if pd.notnull(x) else 'N/A'
                    st.dataframe(user_stats_view.style.format(style_user), height=400)
                
                with user_v_cols[1]:
                    st.markdown("#### 📈 Top İstifadəçilər (Xərcə görə)")
                    top10 = user_stats_view.head(10)
                    if not top10.empty:
                        y_labels = [f"{idx[0]} {idx[1]}" for idx in top10.index]
                        fig_top_u = px.bar(top10, y=y_labels, x='Cəmi Xərc', orientation='h', title="Top 10 Xərc Edən")
                        fig_top_u.update_layout(yaxis_title="İstifadəçi", xaxis_title="Cəmi Xərc (AZN)")
                        st.plotly_chart(fig_top_u, use_container_width=True)
            else:
                st.info("İstifadəçi aktivliyi göstərmək üçün məlumat yoxdur.")
            
            st.markdown("--- \n #### 🔧 İstifadəçi Alətləri (Gələcəkdə)")
            tool_u_cols = st.columns(3)
            tool_u_cols[0].button("📧 Kütləvi Bildiriş", disabled=True, key="mass_notify_u")
            tool_u_cols[1].button("📊 Fərdi Hesabatlar", disabled=True, key="user_reports_u")
            tool_u_cols[2].button("🔑 Giriş İdarəetməsi", disabled=True, key="access_mgmt_u")


        # 7. SİSTEM ALƏTLƏRİ TAB
        with admin_tabs_obj[6]:
            st.markdown("### "+ admin_tab_names[6])
            tool_sys_cols = st.columns(2)
            with tool_sys_cols[0]:
                st.markdown("#### 🧹 Məlumat Təmizliyi")
                if st.button("🔍 Bütün Tam Dublikatları Tap", key="find_full_dup_tool"):
                    df_tool = load_trip_data()
                    if not df_tool.empty:
                        full_dups = df_tool[df_tool.duplicated(keep=False)]
                        st.info(f"{len(full_dups)} tam dublikat qeyd tapıldı.")
                        if not full_dups.empty: st.dataframe(full_dups.head())
                
                if st.button("🔍 Boş Sahələri Analiz Et", key="analyze_empty_tool"):
                    df_tool2 = load_trip_data()
                    if not df_tool2.empty:
                        nulls = df_tool2.isnull().sum()
                        nulls = nulls[nulls > 0]
                        if not nulls.empty: st.warning(f"Boş sahələr:\n{nulls.to_string()}")
                        else: st.success("Boş sahə tapılmadı.")
            
            with tool_sys_cols[1]:
                st.markdown("#### 💾 Backup və Sistem Məlumatları")
                if st.button("📥 Manuel Backup Yarat (Excel)", key="man_backup_tool"):
                    df_tool3 = load_trip_data()
                    if not df_tool3.empty:
                        buffer_bck = BytesIO()
                        df_tool3.to_excel(buffer_bck, index=False, engine='openpyxl')
                        st.download_button("⬇️ Backup Faylını Yüklə", buffer_bck.getvalue(), f"backup_ezamiyyet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "application/vnd.ms-excel")
                        write_log("Manuel backup yaradıldı", user="admin")
                    else: st.warning("Backup üçün məlumat yoxdur.")
                
                if st.button("ℹ️ Sistem Məlumatları", key="sys_info_tool"):
                    df_tool4 = load_trip_data()
                    fsize = (os.path.getsize("ezamiyyet_melumatlari.xlsx")/1024) if os.path.exists("ezamiyyet_melumatlari.xlsx") else 0
                    st.metric("Excel Fayl Ölçüsü", f"{fsize:.2f} KB")
                    st.metric("Qeyd Sayı", len(df_tool4))
            
            st.markdown("#### 📜 Sistem Logları")
            if st.checkbox("Son 10 Logu Göstər", key="show_logs_tool"):
                if os.path.exists("admin_logs.json"):
                    try:
                        with open("admin_logs.json", "r", encoding="utf-8") as f_log:
                            logs_data = json.load(f_log)
                        st.json(logs_data[-10:]) # Show last 10 logs
                    except Exception as e_log_read:
                        st.error(f"Log faylını oxuma xətası: {e_log_read}")
                else:
                    st.info("Log faylı tapılmadı.")


            st.markdown("#### ⚠️ Kritik Əməliyyatlar (Diqqətli Olun!)")
            st.warning("🚨 Bu əməliyyatlar geri qaytarıla bilməz!")
            
            crit_cols = st.columns(2)
            with crit_cols[0]:
                if st.button("🗑️ BÜTÜN Ezamiyyət Məlumatlarını Sil", type="destructive", key="del_all_data_tool_btn"):
                    st.session_state.confirm_delete_all_prompt = True
            
            if st.session_state.get('confirm_delete_all_prompt'):
                st.error("Bütün ezamiyyət məlumatlarını silmək istədiyinizə əminsinizmi?")
                confirm_text_del = st.text_input("Təsdiq üçün 'HAMISINI SİL' yazın", key="confirm_del_all_text_tool").strip()
                del_confirm_cols = st.columns(2)
                if del_confirm_cols[0].button("Bəli, Silinsin", type="destructive", key="confirm_del_all_final_tool"):
                    if confirm_text_del == "HAMISINI SİL":
                        if os.path.exists("ezamiyyet_melumatlari.xlsx"): os.remove("ezamiyyet_melumatlari.xlsx")
                        st.success("✅ Bütün məlumatlar silindi!")
                        write_log("KRİTİK: Bütün məlumatlar silindi", user="admin")
                        st.session_state.confirm_delete_all_prompt = False
                        st.cache_data.clear()
                        st.rerun()
                    else: st.warning("Təsdiq mətni yanlışdır.")
                if del_confirm_cols[1].button("Xeyr, Ləğv Et (Silmə)", key="cancel_del_all_tool"):
                    st.session_state.confirm_delete_all_prompt = False
                    st.rerun()
                st.stop()


            with crit_cols[1]:
                if st.button("🔄 Sistemi Sıfırla (Sessiya, Konfiq, Loglar)", type="destructive", key="reset_sys_tool_btn"):
                     st.session_state.confirm_reset_system_prompt = True

            if st.session_state.get('confirm_reset_system_prompt'):
                st.error("Sistemi sıfırlamaq istədiyinizə əminsinizmi? (Sessiya, Konfiq, Loglar silinəcək, əsas məlumat faylına toxunulmayacaq)")
                confirm_text_reset = st.text_input("Təsdiq üçün 'SİSTEMİ SIFIRLA' yazın", key="confirm_reset_sys_text_tool").strip()
                reset_confirm_cols = st.columns(2)
                if reset_confirm_cols[0].button("Bəli, Sıfırlansın", type="destructive", key="confirm_reset_final_tool"):
                    if confirm_text_reset == "SİSTEMİ SIFIRLA":
                        keys_to_clear = [k for k in st.session_state.keys()] # Get all keys
                        for key in keys_to_clear: del st.session_state[key]
                        if os.path.exists("system_config.json"): os.remove("system_config.json")
                        if os.path.exists("admin_logs.json"): os.remove("admin_logs.json")
                        st.success("✅ Sistem sıfırlandı! Yenidən giriş edin.")
                        write_log("KRİTİK: Sistem sıfırlandı (sessiya, konfiq, loglar)", user="admin")
                        st.session_state.confirm_reset_system_prompt = False
                        st.rerun()
                    else: st.warning("Təsdiq mətni yanlışdır.")
                if reset_confirm_cols[1].button("Xeyr, Ləğv Et (Sıfırlama)", key="cancel_reset_sys_tool"):
                    st.session_state.confirm_reset_system_prompt = False
                    st.rerun()
                st.stop()

        # Footer
        st.markdown("---")
        foot_cols = st.columns(3)
        if 'admin_session_time' in st.session_state and isinstance(st.session_state.admin_session_time, datetime):
            foot_cols[0].caption(f"🔐 Admin Sessiyası: {st.session_state.admin_session_time.strftime('%H:%M:%S')}")
        try: foot_cols[1].caption(f"📊 Cəmi məlumat: {len(load_trip_data())} qeyd")
        except: foot_cols[1].caption("📊 Cəmi məlumat: N/A")
        foot_cols[2].caption(f"📅 Panel Yüklənmə: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
