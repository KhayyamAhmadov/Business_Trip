import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json



# 1. İLK STREAMLIT ƏMRİ OLMALIDIR!
st.set_page_config(
    page_title="Ezamiyyət İdarəetmə Sistemi",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
                                  placeholder="Giriş kodunu daxil edin...")
        
        cols = st.columns([1,2,1])
        with cols[1]:
            if st.button("Daxil ol", use_container_width=True):
                if access_code == "admin":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Yanlış giriş kodu!")
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
    
    .dataframe {
        border-radius: 12px!important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05)!important;
    }
</style>
""", unsafe_allow_html=True)

# ============================== SABİTLƏR ==============================
DEPARTMENTS = [
    "Statistika işlərinin əlaqələndirilməsi və strateji planlaşdırma şöbəsi",
    "Keyfiyyətin idarə edilməsi və metaməlumatlar şöbəsi",
    "Milli hesablar və makroiqtisadi göstəricilər statistikası şöbəsi",
    "Kənd təsərrüfatı statistikası şöbəsi",
    "Sənaye və tikinti statistikası şöbəsi",
    "Energetika və ətraf mühit statistikası şöbəsi",
    "Ticarət statistikası şöbəsi",
    "Sosial statistika şöbəsi",
    "Xidmət statistikası şöbəsi",
    "Əmək statistikası şöbəsi",
    "Qiymət statistikası şöbəsi",
    "Əhali statistikası şöbəsi",
    "Həyat keyfiyyətinin statistikası şöbəsi",
    "Dayanıqlı inkişaf statistikası şöbəsi",
    "İnformasiya texnologiyaları şöbəsi",
    "İnformasiya və ictimaiyyətlə əlaqələr şöbəsi",
    "Beynəlxalq əlaqələr şöbəsi",
    "İnsan resursları və hüquq şöbəsi",
    "Maliyyə və təsərrüfat şöbəsi",
    "Ümumi şöbə",
    "Rejim və məxfi kargüzarlıq şöbəsi",
    "Elmi - Tədqiqat və Statistik İnnovasiyalar Mərkəzi",
    "Yerli statistika orqanları"
]

CITIES = [
    "Abşeron", "Ağcabədi", "Ağdam", "Ağdaş", "Ağdərə", "Ağstafa", "Ağsu", "Astara", "Bakı",
    "Babək (Naxçıvan MR)", "Balakən", "Bərdə", "Beyləqan", "Biləsuvar", "Cəbrayıl", "Cəlilabad",
    "Culfa (Naxçıvan MR)", "Daşkəsən", "Füzuli", "Gədəbəy", "Gəncə", "Goranboy", "Göyçay",
    "Göygöl", "Hacıqabul", "Xaçmaz", "Xankəndi", "Xızı", "Xocalı", "Xocavənd", "İmişli",
    "İsmayıllı", "Kəlbəcər", "Kəngərli (Naxçıvan MR)", "Kürdəmir", "Laçın", "Lənkəran",
    "Lerik", "Masallı", "Mingəçevir", "Naftalan", "Neftçala", "Naxçıvan", "Oğuz", "Siyəzən",
    "Ordubad (Naxçıvan MR)", "Qəbələ", "Qax", "Qazax", "Qobustan", "Quba", "Qubadlı",
    "Qusar", "Saatlı", "Sabirabad", "Sədərək (Naxçıvan MR)", "Salyan", "Samux", "Şabran",
    "Şahbuz (Naxçıvan MR)", "Şamaxı", "Şəki", "Şəmkir", "Şərur (Naxçıvan MR)", "Şirvan",
    "Şuşa", "Sumqayıt", "Tərtər", "Tovuz", "Ucar", "Yardımlı", "Yevlax", "Zaqatala",
    "Zəngilan", "Zərdab", "Nabran", "Xudat"
]

COUNTRIES = {
    "Türkiyə": 300,
    "Gürcüstan": 250,
    "Almaniya": 600,
    "BƏƏ": 500,
    "Rusiya": 400,
    "İran": 280,
    "İtaliya": 550,
    "Fransa": 580,
    "İngiltərə": 620,
    "ABŞ": 650
}

DOMESTIC_ROUTES = {
    ("Bakı", "Ağcabədi"): 10.50,
    ("Bakı", "Ağdam"): 13.50,
    ("Bakı", "Ağdaş"): 10.30,
    ("Bakı", "Astara"): 10.40,
    ("Bakı", "Şuşa"): 28.90,
    ("Bakı", "Balakən"): 17.30,
    ("Bakı", "Beyləqan"): 10.00,
    ("Bakı", "Bərdə"): 11.60,
    ("Bakı", "Biləsuvar"): 6.50,
    ("Bakı", "Cəlilabad"): 7.10,
    ("Bakı", "Füzuli"): 10.80,
    ("Bakı", "Gədəbəy"): 16.50,
    ("Bakı", "Gəncə"): 13.10,
    ("Bakı", "Goranboy"): 9.40,
    ("Bakı", "Göyçay"): 9.20,
    ("Bakı", "Göygöl"): 13.50,
    ("Bakı", "İmişli"): 8.10,
    ("Bakı", "İsmayıllı"): 7.00,
    ("Bakı", "Kürdəmir"): 7.10,
    ("Bakı", "Lənkəran"): 8.80,
    ("Bakı", "Masallı"): 7.90,
    ("Bakı", "Mingəçevir"): 11.40,
    ("Bakı", "Naftalan"): 12.20,
    ("Bakı", "Oğuz"): 13.10,
    ("Bakı", "Qax"): 14.60,
    ("Bakı", "Qazax"): 17.60,
    ("Bakı", "Qəbələ"): 11.50,
    ("Bakı", "Quba"): 5.90,
    ("Bakı", "Qusar"): 6.40,
    ("Bakı", "Saatlı"): 7.10,
    ("Bakı", "Sabirabad"): 6.10,
    ("Bakı", "Şəki"): 13.20,
    ("Bakı", "Şəmkir"): 15.00,
    ("Bakı", "Siyəzən"): 3.60,
    ("Bakı", "Tərtər"): 12.20,
    ("Bakı", "Tovuz"): 16.40,
    ("Bakı", "Ucar"): 8.90,
    ("Bakı", "Xaçmaz"): 5.50,
    ("Bakı", "Nabran"): 7.20,
    ("Bakı", "Xudat"): 6.30,
    ("Bakı", "Zaqatala"): 15.60,
    ("Bakı", "Zərdab"): 9.30
}

PAYMENT_TYPES = {
    "Ödənişsiz": 0,
    "10% ödəniş edilməklə": 0.1,
    "Tam ödəniş edilməklə": 1
}

# ============================== FUNKSİYALAR ==============================
def load_trip_data():
    """Ezamiyyət məlumatlarını yükləyir"""
    try:
        if os.path.exists("ezamiyyet_melumatlari.xlsx"):
            # Explicitly parse date columns
            df = pd.read_excel(
                "ezamiyyet_melumatlari.xlsx",
                parse_dates=['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            )
            
            # Ensure proper datetime conversion for all date columns
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

def check_admin_session():
    if 'admin_session_time' in st.session_state:
        if datetime.now() - st.session_state.admin_session_time > timedelta(minutes=30):
            st.session_state.admin_logged = False
            return False
    return True

def load_system_config():
    try:
        if os.path.exists("system_config.json"):
            with open("system_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def write_log(action, details=""):
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "user": "admin"
        }
        
        log_file = "admin_logs.json"
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        pass

def load_trip_data():
    """Ezamiyyət məlumatlarını yükləyir"""
    try:
        if os.path.exists("ezamiyyet_melumatlari.xlsx"):
            df = pd.read_excel("ezamiyyet_melumatlari.xlsx")
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Məlumat yükləmə xətası: {str(e)}")
        return pd.DataFrame()

def calculate_domestic_amount(from_city, to_city):
    """Daxili marşrut üçün bilet qiymətini hesablayır"""
    return DOMESTIC_ROUTES.get((from_city, to_city), 70)

def calculate_days(start_date, end_date):
    """İki tarix arasındakı günləri hesablayır"""
    return (end_date - start_date).days + 1

def calculate_total_amount(daily_allowance, days, payment_type, ticket_price=0):
    """Ümumi məbləği hesablayır"""
    return (daily_allowance * days + ticket_price) * PAYMENT_TYPES[payment_type]

def save_trip_data(data):
    """Ezamiyyət məlumatlarını saxlayır"""
    try:
        df_new = pd.DataFrame([data])
        try:
            df_existing = pd.read_excel("ezamiyyet_melumatlari.xlsx")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new
        df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
        return True
    except Exception as e:
        st.error(f"Yadda saxlama xətası: {str(e)}")
        return False

# ƏSAS İNTERFEYS
st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli"])

# YENİ EZAMİYYƏT HISSESI
with tab1:
    with st.container():
        col1, col2 = st.columns([2, 1], gap="large")
        
        # Sol Sütun
        with col1:
            with st.expander("👤 Şəxsi Məlumatlar", expanded=True):
                cols = st.columns(2)
                with cols[0]:
                    first_name = st.text_input("Ad")
                    father_name = st.text_input("Ata adı")
                with cols[1]:
                    last_name = st.text_input("Soyad")
                    position = st.text_input("Vəzifə")

            with st.expander("🏢 Təşkilat Məlumatları"):
                department = st.selectbox("Şöbə", DEPARTMENTS)

            with st.expander("🧳 Ezamiyyət Detalları"):
                trip_type = st.radio("Növ", ["Ölkə daxili", "Ölkə xarici"])
                payment_type = st.selectbox("Ödəniş növü", list(PAYMENT_TYPES.keys()))
                
                if trip_type == "Ölkə daxili":
                    cols = st.columns(2)
                    with cols[0]:
                        from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"))
                    with cols[1]:
                        to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city])
                    ticket_price = calculate_domestic_amount(from_city, to_city)
                    daily_allowance = 70
                    accommodation = "Tətbiq edilmir"
                else:
                    country = st.selectbox("Ölkə", list(COUNTRIES.keys()))
                    payment_mode = st.selectbox(
                        "Ödəniş rejimi",
                        options=["Adi rejim", "Günlük Normaya 50% əlavə", "Günlük Normaya 30% əlavə"]
                    )
                    accommodation = st.selectbox(
                        "Qonaqlama xərcləri",
                        options=["Adi rejim", "Yalnız yaşayış yeri ilə təmin edir", "Yalnız gündəlik xərcləri təmin edir"]
                    )
                    base_allowance = COUNTRIES[country]
                    if payment_mode == "Adi rejim":
                        daily_allowance = base_allowance
                    elif payment_mode == "Günlük Normaya 50% əlavə":
                        daily_allowance = base_allowance * 1.5
                    else:
                        daily_allowance = base_allowance * 1.3
                    ticket_price = 0
                    from_city = "Bakı"
                    to_city = country

                cols = st.columns(2)
                with cols[0]:
                    start_date = st.date_input("Başlanğıc tarixi")
                with cols[1]:
                    end_date = st.date_input("Bitmə tarixi")
                
                purpose = st.text_area("Ezamiyyət məqsədi")

        # Sağ Sütun (Hesablama)
        with col2:
            with st.container():
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                
                if start_date and end_date and end_date >= start_date:
                    trip_days = calculate_days(start_date, end_date)
                    total_amount = calculate_total_amount(daily_allowance, trip_days, payment_type, ticket_price)
                    
                    # Qonaqlama əmsalı
                    if trip_type == "Ölkə xarici":
                        if accommodation == "Yalnız yaşayış yeri ilə təmin edir":
                            total_amount *= 1.4
                            delta_label = "40% artım (Yaşayış)"
                        elif accommodation == "Yalnız gündəlik xərcləri təmin edir":
                            total_amount *= 1.6
                            delta_label = "60% artım (Gündəlik)"
                        else:
                            delta_label = None
                    else:
                        delta_label = None
                    
                    st.metric("📅 Günlük müavinət", f"{daily_allowance} AZN")
                    if trip_type == "Ölkə daxili":
                        st.metric("🚌 Nəqliyyat xərci", f"{ticket_price} AZN")
                    st.metric("⏳ Müddət", f"{trip_days} gün")
                    st.metric(
                        "💳 Ümumi məbləğ", 
                        f"{total_amount:.2f} AZN", 
                        delta=delta_label,
                        delta_color="normal" if delta_label else "off"
                    )

            if st.button("✅ Yadda Saxla", use_container_width=True):
                if all([first_name, last_name, start_date, end_date]):
                    trip_data = {
                        "Tarix": datetime.now(),  # Store as datetime object
                        "Ad": first_name,
                        "Soyad": last_name,
                        "Ata adı": father_name,
                        "Vəzifə": position,
                        "Şöbə": department,
                        "Ezamiyyət növü": trip_type,
                        "Ödəniş növü": payment_type,
                        "Qonaqlama növü": accommodation,
                        "Marşrut": f"{from_city} → {to_city}",
                        "Bilet qiyməti": ticket_price,
                        "Günlük müavinət": daily_allowance,
                        "Başlanğıc tarixi": start_date,  # datetime.date object
                        "Bitmə tarixi": end_date,        # datetime.date object
                        "Günlər": trip_days,
                        "Ümumi məbləğ": total_amount,
                        "Məqsəd": purpose
                    }
                   
                    if save_trip_data(trip_data):
                        st.success("Məlumatlar yadda saxlandı!")
                        st.balloons()
                else:
                    st.error("Zəhmət olmasa bütün məcburi sahələri doldurun!")

# admin paneli 

# Admin Panel hissəsi - Təkmil versiya
with tab2:
    # Admin sessiya idarəetməsi
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if 'admin_session_time' not in st.session_state:
        st.session_state.admin_session_time = datetime.now()

    # Sessiya müddəti yoxlanışı (30 dəqiqə)
    if st.session_state.admin_logged:
        if datetime.now() - st.session_state.admin_session_time > timedelta(minutes=30):
            st.session_state.admin_logged = False
            st.warning("Sessiya müddəti bitdi. Yenidən giriş edin.")

    # Admin giriş forması
    if not st.session_state.admin_logged:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin: 2rem auto;
            max-width: 500px;
            text-align: center;
        ">
            <h2 style="color: white; margin-bottom: 2rem;">🔐 Admin Panel Giriş</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("admin_login_form"):
                    admin_user = st.text_input("👤 İstifadəçi adı", placeholder="admin")
                    admin_pass = st.text_input("🔒 Şifrə", type="password", placeholder="••••••••")
                    remember_me = st.checkbox("🔄 Məni xatırla")
                    
                    submitted = st.form_submit_button("🚀 Giriş Et", use_container_width=True)
                    
                    if submitted:
                        if admin_user == "admin" and admin_pass == "admin123":
                            st.session_state.admin_logged = True
                            st.session_state.admin_session_time = datetime.now()
                            st.success("✅ Uğurlu giriş!")
                            st.rerun()
                        else:
                            st.error("❌ Yanlış giriş məlumatları!")
        st.stop()

    # Admin Panel Ana Səhifə
    if st.session_state.admin_logged:
        # Header və Navigation
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        ">
            <h1 style="color: white; text-align: center; margin: 0;">
                ⚙️ Admin İdarəetmə Paneli
            </h1>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">
                Ezamiyyət sisteminin tam idarəetməsi
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Session info və çıxış
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.info(f"👋 Xoş gəlmisiniz, Admin! Sessiya: {st.session_state.admin_session_time.strftime('%H:%M')}")
        with col2:
            if st.button("🔄 Sessiya Yenilə"):
                st.session_state.admin_session_time = datetime.now()
                st.success("Sessiya yeniləndi!")
        with col3:
            if st.button("🚪 Çıxış Et", type="secondary"):
                st.session_state.admin_logged = False
                st.rerun()

        # Ana tab bölməsi
        admin_tabs = st.tabs([
            "📊 Dashboard", 
            "🗂️ Məlumat İdarəetməsi", 
            "📈 Analitika", 
            "📥 İdxal/İxrac", 
            "⚙️ Sistem Parametrləri",
            "👥 İstifadəçi İdarəetməsi",
            "🔧 Sistem Alətləri"
        ])

# 1. DASHBOARD TAB
        with admin_tabs[0]:
            try:
                df = load_trip_data()
                
                if not df.empty:
                    # Tarixi sütunları düzəlt - Xəta həlli
                    date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                    for col in date_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
                    
                    # Rəqəmsal sütunları düzəlt - Xəta həlli
                    numeric_cols = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti', 'Günlər']
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    # Əsas metrikalar
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        recent_count = 0
                        if 'Tarix' in df.columns:
                            recent_mask = df['Tarix'] >= (datetime.now() - timedelta(days=30))
                            recent_count = recent_mask.sum()
                        
                        st.metric(
                            "📋 Ümumi Ezamiyyət",
                            len(df),
                            delta=f"+{recent_count}" if recent_count > 0 else None
                        )
                    
                    with col2:
                        total_amount = df['Ümumi məbləğ'].sum() if 'Ümumi məbləğ' in df.columns else 0
                        avg_amount = total_amount / len(df) if len(df) > 0 and total_amount > 0 else 0
                        
                        st.metric(
                            "💰 Ümumi Xərclər",
                            f"{total_amount:,.2f} AZN",
                            delta=f"{avg_amount:.2f} AZN orta"
                        )
                    
                    with col3:
                        if 'Günlər' in df.columns and df['Günlər'].notna().any():
                            avg_days = df['Günlər'].mean()
                            st.metric("⏱️ Orta Müddət", f"{avg_days:.1f} gün")
                        else:
                            st.metric("⏱️ Orta Müddət", "N/A")
                    
                    with col4:
                        active_users = 0
                        if 'Ad' in df.columns:
                            active_users = df['Ad'].nunique()
                        st.metric("👥 Aktiv İstifadəçilər", active_users)
                    
                    with col5:
                        international_pct = 0
                        if 'Ezamiyyət növü' in df.columns:
                            international_pct = (df['Ezamiyyət növü'] == 'Ölkə xarici').mean() * 100
                        st.metric("🌍 Beynəlxalq %", f"{international_pct:.1f}%")

                    # Son fəaliyyətlər - Xəta həlli
                    st.markdown("### 📅 Son Ezamiyyətlər")
                    
                    # Sıralama üçün təhlükəsiz yanaşma
                    display_df = df.copy()
                    if 'Tarix' in display_df.columns:
                        display_df = display_df.sort_values('Tarix', ascending=False, na_position='last')
                    
                    recent_trips = display_df.head(10)
                    
                    if len(recent_trips) > 0:
                        for idx, row in recent_trips.iterrows():
                            with st.container():
                                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                                
                                with col1:
                                    ad = row.get('Ad', 'N/A') if pd.notna(row.get('Ad')) else 'N/A'
                                    soyad = row.get('Soyad', 'N/A') if pd.notna(row.get('Soyad')) else 'N/A'
                                    st.write(f"**{ad} {soyad}**")
                                    
                                    sobe = row.get('Şöbə', 'N/A') if pd.notna(row.get('Şöbə')) else 'N/A'
                                    sobe_short = sobe[:50] + "..." if len(str(sobe)) > 50 else sobe
                                    st.caption(sobe_short)
                                
                                with col2:
                                    marsrut = row.get('Marşrut', 'N/A') if pd.notna(row.get('Marşrut')) else 'N/A'
                                    st.write(f"📍 {marsrut}")
                                    
                                    bas_tarix = row.get('Başlanğıc tarixi', 'N/A')
                                    if pd.notna(bas_tarix) and bas_tarix != 'N/A':
                                        try:
                                            formatted_date = pd.to_datetime(bas_tarix).strftime('%d.%m.%Y')
                                            st.caption(f"🗓️ {formatted_date}")
                                        except:
                                            st.caption(f"🗓️ {bas_tarix}")
                                    else:
                                        st.caption("🗓️ N/A")
                                
                                with col3:
                                    mebleg = row.get('Ümumi məbləğ', 0)
                                    mebleg = float(mebleg) if pd.notna(mebleg) else 0
                                    st.write(f"💰 {mebleg:.2f} AZN")
                                
                                with col4:
                                    odenis = row.get('Ödəniş növü', 'N/A') if pd.notna(row.get('Ödəniş növü')) else 'N/A'
                                    status_color = "🟢" if odenis == "Ödənişsiz" else "🟡"
                                    st.write(f"{status_color} {odenis}")
                                
                                st.divider()
                    else:
                        st.info("📝 Göstəriləcək ezamiyyət yoxdur")

                    # Qrafiklər - Xəta həlli
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'Ezamiyyət növü' in df.columns and df['Ezamiyyət növü'].notna().any():
                            ezamiyyet_stats = df['Ezamiyyət növü'].value_counts()
                            if len(ezamiyyet_stats) > 0:
                                fig = px.pie(
                                    values=ezamiyyet_stats.values,
                                    names=ezamiyyet_stats.index,
                                    title='🌍 Ezamiyyət Növləri Payı',
                                    color_discrete_sequence=['#667eea', '#764ba2'],
                                    hole=0.4
                                )
                                fig.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("📊 Ezamiyyət növü məlumatı yoxdur")
                        else:
                            st.info("📊 Ezamiyyət növü sütunu yoxdur")
                    
                    with col2:
                        if 'Ödəniş növü' in df.columns and df['Ödəniş növü'].notna().any():
                            payment_stats = df['Ödəniş növü'].value_counts()
                            if len(payment_stats) > 0:
                                fig = px.bar(
                                    x=payment_stats.index,
                                    y=payment_stats.values,
                                    title='💳 Ödəniş Növləri',
                                    color=payment_stats.values,
                                    color_continuous_scale='Blues'
                                )
                                fig.update_layout(showlegend=False)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("📊 Ödəniş növü məlumatı yoxdur")
                        else:
                            st.info("📊 Ödəniş növü sütunu yoxdur")

                else:
                    st.warning("📭 Hələ heç bir ezamiyyət qeydiyyatı yoxdur")
                    st.info("🚀 Sistemə ilk ezamiyyəti əlavə etmək üçün 'Yeni Ezamiyyət' bölməsinə keçin")
                    
            except Exception as e:
                st.error(f"❌ Dashboard yüklənərkən xəta: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

        # 2. MƏLUMAT İDARƏETMƏSİ TAB
    with admin_tabs[1]:
                st.markdown("### 🗂️ Məlumatların İdarə Edilməsi")
                
                try:
                    df = load_trip_data()
                    
                    if not df.empty:
                        # Məlumat təmizliyi
                        df = df.copy()
                        
                        # Tarixi sütunları təhlükəsiz düzəlt
                        date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                        for col in date_columns:
                            if col in df.columns:
                                df[col] = pd.to_datetime(df[col], errors='coerce')
                        
                        # Dublikatları tapma və silmə bölməsi
                        st.markdown("#### 🔍 Dublikat Təhlili")
                        
                        # Dublikat axtarışı üçün sütun seçimi
                        duplicate_columns = st.multiselect(
                            "Dublikat axtarışı üçün sütunları seçin",
                            options=df.columns.tolist(),
                            default=['Ad', 'Soyad', 'Başlanğıc tarixi', 'Marşrut'] if all(col in df.columns for col in ['Ad', 'Soyad', 'Başlanğıc tarixi', 'Marşrut']) else df.columns.tolist()[:4],
                            help="Bu sütunlarda eyni dəyərlər olan qeydlər dublikat hesab ediləcək"
                        )
                        
                        if duplicate_columns:
                            # Dublikatları tap
                            duplicates_mask = df.duplicated(subset=duplicate_columns, keep=False)
                            duplicates_df = df[duplicates_mask].copy()
                            
                            if len(duplicates_df) > 0:
                                st.warning(f"⚠️ {len(duplicates_df)} dublikat qeyd tapıldı!")
                                
                                # Dublikat qruplarını göstər
                                duplicate_groups = df[duplicates_mask].groupby(duplicate_columns, dropna=False)
                                
                                with st.expander(f"🔍 Dublikat Qeydlər ({len(duplicate_groups)} qrup)", expanded=False):
                                    for name, group in duplicate_groups:
                                        if len(group) > 1:
                                            st.markdown(f"**Qrup:** {', '.join([f'{col}: {val}' for col, val in zip(duplicate_columns, name) if pd.notna(val)])}")
                                            
                                            # Seçilmiş sütunları göstər
                                            display_cols = []
                                            preferred_display = ['Ad', 'Soyad', 'Şöbə', 'Marşrut', 'Başlanğıc tarixi', 'Ümumi məbləğ']
                                            for col in preferred_display:
                                                if col in group.columns:
                                                    display_cols.append(col)
                                            
                                            if not display_cols:
                                                display_cols = group.columns.tolist()[:6]
                                            
                                            st.dataframe(group[display_cols], use_container_width=True, hide_index=False)
                                            st.markdown("---")
                                
                                # Dublikat silmə seçimləri
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    duplicate_strategy = st.selectbox(
                                        "Dublikat silmə strategiyası",
                                        [
                                            "İlk qeydi saxla",
                                            "Son qeydi saxla", 
                                            "Ən yüksək məbləği saxla",
                                            "Ən aşağı məbləği saxla",
                                            "Manuel seçim"
                                        ]
                                    )
                                
                                with col2:
                                    if st.button("🧹 Dublikatları Təmizlə", type="primary"):
                                        try:
                                            if duplicate_strategy == "İlk qeydi saxla":
                                                cleaned_df = df.drop_duplicates(subset=duplicate_columns, keep='first')
                                                removed_count = len(df) - len(cleaned_df)
                                                
                                            elif duplicate_strategy == "Son qeydi saxla":
                                                cleaned_df = df.drop_duplicates(subset=duplicate_columns, keep='last')
                                                removed_count = len(df) - len(cleaned_df)
                                                
                                            elif duplicate_strategy == "Ən yüksək məbləği saxla":
                                                if 'Ümumi məbləğ' in df.columns:
                                                    # Hər qrup üçün ən yüksək məbləği olan qeydi saxla
                                                    idx_to_keep = df.groupby(duplicate_columns, dropna=False)['Ümumi məbləğ'].idxmax()
                                                    cleaned_df = df.loc[idx_to_keep].drop_duplicates()
                                                    # Dublikat olmayanları da əlavə et
                                                    non_duplicates = df[~duplicates_mask]
                                                    cleaned_df = pd.concat([cleaned_df, non_duplicates]).drop_duplicates()
                                                    removed_count = len(df) - len(cleaned_df)
                                                else:
                                                    st.error("'Ümumi məbləğ' sütunu tapılmadı!")
                                                    continue
                                                    
                                            elif duplicate_strategy == "Ən aşağı məbləği saxla":
                                                if 'Ümumi məbləğ' in df.columns:
                                                    # Hər qrup üçün ən aşağı məbləği olan qeydi saxla
                                                    idx_to_keep = df.groupby(duplicate_columns, dropna=False)['Ümumi məbləğ'].idxmin()
                                                    cleaned_df = df.loc[idx_to_keep].drop_duplicates()
                                                    # Dublikat olmayanları da əlavə et
                                                    non_duplicates = df[~duplicates_mask]
                                                    cleaned_df = pd.concat([cleaned_df, non_duplicates]).drop_duplicates()
                                                    removed_count = len(df) - len(cleaned_df)
                                                else:
                                                    st.error("'Ümumi məbləğ' sütunu tapılmadı!")
                                                    continue
                                            
                                            elif duplicate_strategy == "Manuel seçim":
                                                st.info("Manuel seçim üçün aşağıdakı bölmədən qeydləri seçin və silin.")
                                                continue
                                            
                                            # Təsdiq soruşu
                                            if st.checkbox(f"⚠️ {removed_count} dublikat qeydin silinməsini təsdiq edirəm"):
                                                # Faylı yenilə
                                                cleaned_df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                                st.success(f"✅ {removed_count} dublikat qeyd silindi!")
                                                time.sleep(2)
                                                st.rerun()
                                                
                                        except Exception as clean_error:
                                            st.error(f"❌ Dublikat təmizləmə xətası: {str(clean_error)}")
                                            st.code(traceback.format_exc())
                            
                            else:
                                st.success("✅ Dublikat qeyd tapılmadı!")
                        
                        st.markdown("---")
                        
                        # Filtr və axtarış seçimləri
                        st.markdown("#### 🔍 Filtr və Axtarış")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Tarix filtri
                            date_filter = st.selectbox(
                                "📅 Tarix filtri",
                                ["Hamısı", "Son 7 gün", "Son 30 gün", "Son 3 ay", "Bu il", "Seçilmiş aralıq"]
                            )
                            
                            start_date = None
                            end_date = None
                            if date_filter == "Seçilmiş aralıq":
                                start_date = st.date_input("Başlanğıc tarixi")
                                end_date = st.date_input("Bitmə tarixi")
                        
                        with col2:
                            # Şöbə filtri
                            selected_dept = "Hamısı"
                            if 'Şöbə' in df.columns:
                                unique_depts = df['Şöbə'].dropna().unique().tolist()
                                departments = ["Hamısı"] + sorted([str(d) for d in unique_depts])
                                selected_dept = st.selectbox("🏢 Şöbə filtri", departments)
                        
                        with col3:
                            # Ezamiyyət növü filtri
                            selected_type = "Hamısı"
                            if 'Ezamiyyət növü' in df.columns:
                                unique_types = df['Ezamiyyət növü'].dropna().unique().tolist()
                                trip_types = ["Hamısı"] + [str(t) for t in unique_types]
                                selected_type = st.selectbox("✈️ Ezamiyyət növü", trip_types)
                        
                        # Axtarış qutusu
                        search_term = st.text_input("🔎 Ad və ya soyad üzrə axtarış")
                        
                        # Filtirləmə tətbiqi - Xəta həlli
                        filtered_df = df.copy()
                        
                        # Tarix filtri tətbiqi
                        if date_filter != "Hamısı" and 'Tarix' in df.columns:
                            now = datetime.now()
                            
                            try:
                                if date_filter == "Son 7 gün":
                                    mask = filtered_df['Tarix'] >= (now - timedelta(days=7))
                                    filtered_df = filtered_df[mask | filtered_df['Tarix'].isna()]
                                elif date_filter == "Son 30 gün":
                                    mask = filtered_df['Tarix'] >= (now - timedelta(days=30))
                                    filtered_df = filtered_df[mask | filtered_df['Tarix'].isna()]
                                elif date_filter == "Son 3 ay":
                                    mask = filtered_df['Tarix'] >= (now - timedelta(days=90))
                                    filtered_df = filtered_df[mask | filtered_df['Tarix'].isna()]
                                elif date_filter == "Bu il":
                                    mask = filtered_df['Tarix'].dt.year == now.year
                                    filtered_df = filtered_df[mask | filtered_df['Tarix'].isna()]
                                elif date_filter == "Seçilmiş aralıq" and start_date and end_date:
                                    start_datetime = pd.to_datetime(start_date)
                                    end_datetime = pd.to_datetime(end_date)
                                    mask = (filtered_df['Tarix'] >= start_datetime) & (filtered_df['Tarix'] <= end_datetime)
                                    filtered_df = filtered_df[mask | filtered_df['Tarix'].isna()]
                            except Exception as date_error:
                                st.warning(f"⚠️ Tarix filtri xətası: {str(date_error)}")
                        
                        # Şöbə filtri
                        if selected_dept != "Hamısı" and 'Şöbə' in filtered_df.columns:
                            mask = filtered_df['Şöbə'].astype(str) == selected_dept
                            filtered_df = filtered_df[mask | filtered_df['Şöbə'].isna()]
                        
                        # Ezamiyyət növü filtri
                        if selected_type != "Hamısı" and 'Ezamiyyət növü' in filtered_df.columns:
                            mask = filtered_df['Ezamiyyət növü'].astype(str) == selected_type
                            filtered_df = filtered_df[mask | filtered_df['Ezamiyyət növü'].isna()]
                        
                        # Axtarış filtri
                        if search_term:
                            search_mask = pd.Series([False] * len(filtered_df))
                            
                            if 'Ad' in filtered_df.columns:
                                ad_mask = filtered_df['Ad'].astype(str).str.contains(search_term, case=False, na=False)
                                search_mask = search_mask | ad_mask
                            
                            if 'Soyad' in filtered_df.columns:
                                soyad_mask = filtered_df['Soyad'].astype(str).str.contains(search_term, case=False, na=False)
                                search_mask = search_mask | soyad_mask
                            
                            filtered_df = filtered_df[search_mask]
                        
                        # Nəticələr
                        st.markdown(f"#### 📊 Nəticələr ({len(filtered_df)} qeyd)")
                        
                        if len(filtered_df) > 0:
                            # Sütun seçimi
                            available_columns = filtered_df.columns.tolist()
                            default_columns = []
                            
                            # Mövcud sütunları yoxla və default siyahısını yarat
                            preferred_cols = ['Ad', 'Soyad', 'Şöbə', 'Marşrut', 'Ümumi məbləğ', 'Başlanğıc tarixi']
                            for col in preferred_cols:
                                if col in available_columns:
                                    default_columns.append(col)
                            
                            # Əgər default sütun yoxdursa, ilk 5 sütunu götür
                            if len(default_columns) == 0:
                                default_columns = available_columns[:5]
                            
                            selected_columns = st.multiselect(
                                "Göstəriləcək sütunları seçin",
                                available_columns,
                                default=default_columns
                            )
                            
                            if selected_columns:
                                try:
                                    display_df = filtered_df[selected_columns].copy()
                                    
                                    # Sütun konfiqurasiyası - Xəta həlli
                                    column_config = {}
                                    for col in selected_columns:
                                        if col in ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']:
                                            column_config[col] = st.column_config.DatetimeColumn(
                                                col,
                                                format="DD.MM.YYYY" if col != 'Tarix' else "DD.MM.YYYY HH:mm"
                                            )
                                        elif col in ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']:
                                            column_config[col] = st.column_config.NumberColumn(
                                                col,
                                                format="%.2f AZN",
                                                min_value=0
                                            )
                                    
                                    # NaN dəyərləri təmizlə
                                    for col in display_df.columns:
                                        if display_df[col].dtype == 'object':
                                            display_df[col] = display_df[col].fillna('')
                                        else:
                                            display_df[col] = display_df[col].fillna(0)
                                    
                                    # Redaktə edilə bilən cədvəl
                                    edited_df = st.data_editor(
                                        display_df,
                                        column_config=column_config,
                                        use_container_width=True,
                                        height=400,
                                        key="admin_data_editor",
                                        hide_index=True
                                    )
                                    
                                    # Dəyişiklikləri saxlama
                                    if st.button("💾 Dəyişiklikləri Saxla", type="primary"):
                                        try:
                                            # Tarixi sütunları yoxla və düzəlt
                                            date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
                                            for col in date_columns:
                                                if col in edited_df.columns:
                                                    edited_df[col] = pd.to_datetime(edited_df[col], errors='coerce')
                                    
                                            # Rəqəmsal sütunları yoxla və düzəlt
                                            numeric_columns = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']
                                            for col in numeric_columns:
                                                if col in edited_df.columns:
                                                    edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0)
                                    
                                            # Redaktə olunmuş məlumatları əsas DataFrame-ə tətbiq et
                                            for idx in edited_df.index:
                                                if idx in df.index:
                                                    for col in selected_columns:
                                                        df.loc[idx, col] = edited_df.loc[idx, col]
                                            
                                            # Faylı yenilə
                                            df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                            st.success("✅ Dəyişikliklər saxlanıldı!")
                                            time.sleep(2)
                                            st.rerun()
                                            
                                        except Exception as save_error:
                                            st.error(f"❌ Saxlama xətası: {str(save_error)}")
                                            st.code(traceback.format_exc())
                                    
                                except Exception as display_error:
                                    st.error(f"❌ Cədvəl göstərmə xətası: {str(display_error)}")
                                    st.write("Ham məlumat:")
                                    st.dataframe(filtered_df[selected_columns])
                                
                                # Kütləvi əməliyyatlar
                                st.markdown("#### ⚡ Kütləvi Əməliyyatlar")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if st.button("📤 Seçilmiş qeydləri ixrac et"):
                                        try:
                                            csv = filtered_df[selected_columns].to_csv(index=False).encode('utf-8')
                                            st.download_button(
                                                "⬇️ CSV Yüklə",
                                                data=csv,
                                                file_name=f"filtrlenmis_ezamiyyetler_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                                mime="text/csv"
                                            )
                                        except Exception as export_error:
                                            st.error(f"❌ İxrac xətası: {str(export_error)}")
                                
                                with col2:
                                    # Silmək üçün qeyd seçimi
                                    if len(filtered_df) > 0:
                                        # Təhlükəsiz format funksiyası
                                        def safe_format_record(idx, row):
                                            try:
                                                ad = str(row.get('Ad', 'N/A')) if pd.notna(row.get('Ad')) else 'N/A'
                                                soyad = str(row.get('Soyad', 'N/A')) if pd.notna(row.get('Soyad')) else 'N/A'
                                                marsrut = str(row.get('Marşrut', 'N/A')) if pd.notna(row.get('Marşrut')) else 'N/A'
                                                return f"{ad} {soyad} - {marsrut}"
                                            except:
                                                return f"Qeyd #{idx}"
                                        
                                        selected_indices = st.multiselect(
                                            "Silinəcək qeydləri seçin",
                                            options=filtered_df.index.tolist(),
                                            format_func=lambda x: safe_format_record(x, filtered_df.loc[x])
                                        )
                                
                                with col3:
                                    if selected_indices and st.button("🗑️ Seçilmiş qeydləri sil", type="secondary"):
                                        if st.checkbox("⚠️ Silmə əməliyyatını təsdiq edirəm"):
                                            try:
                                                df_updated = df.drop(selected_indices)
                                                df_updated.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                                st.success(f"✅ {len(selected_indices)} qeyd silindi!")
                                                time.sleep(2)
                                                st.rerun()
                                            except Exception as delete_error:
                                                st.error(f"❌ Silinmə xətası: {str(delete_error)}")
                            
                            else:
                                st.warning("Zəhmət olmasa göstəriləcək sütunları seçin")
                        
                        else:
                            st.info("🔍 Filtrə uyğun qeyd tapılmadı")
                    
                    else:
                        st.warning("📭 Hələ heç bir məlumat yoxdur")
                        
                except Exception as e:
                    st.error(f"❌ Məlumat idarəetməsi xətası: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


        # 3. ANALİTİKA TAB
    with admin_tabs[2]:
        st.markdown("### 📈 Detallı Analitika və Hesabatlar")            
        try:
            df = load_trip_data()
            
            if not df.empty:
                # Tarixi məlumatları hazırla
                if 'Tarix' in df.columns:
                    df['Tarix'] = pd.to_datetime(df['Tarix'], errors='coerce')
                    df['Ay'] = df['Tarix'].dt.to_period('M')
                    df['Həftə'] = df['Tarix'].dt.to_period('W')
                
                # Rəqəmsal sütunları hazırla
                numeric_cols = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                # Analitik seçimlər
                analysis_type = st.selectbox(
                    "📊 Analiz növü",
                    ["Zaman Analizi", "Şöbə Analizi", "Coğrafi Analiz", "Maliyyə Analizi", "Məqsəd Analizi"]
                )

                if analysis_type == "Zaman Analizi":
                    st.markdown("#### 📅 Zamansal Trendlər")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Aylıq trend
                        if 'Ay' in df.columns:
                            monthly_stats = df.groupby('Ay').agg({
                                'Ümumi məbləğ': 'sum',
                                'Ad': 'count'
                            }).rename(columns={'Ad': 'Ezamiyyət sayı'})
                            
                            fig = make_subplots(specs=[[{"secondary_y": True}]])
                            
                            fig.add_trace(
                                go.Bar(
                                    x=[str(x) for x in monthly_stats.index],
                                    y=monthly_stats['Ümumi məbləğ'],
                                    name="Xərclər (AZN)",
                                    marker_color='lightblue'
                                ),
                                secondary_y=False,
                            )
                            
                            fig.add_trace(
                                go.Scatter(
                                    x=[str(x) for x in monthly_stats.index],
                                    y=monthly_stats['Ezamiyyət sayı'],
                                    mode='lines+markers',
                                    name="Ezamiyyət sayı",
                                    line=dict(color='red')
                                ),
                                secondary_y=True,
                            )
                            
                            fig.update_xaxes(title_text="Ay")
                            fig.update_yaxes(title_text="Xərclər (AZN)", secondary_y=False)
                            fig.update_yaxes(title_text="Ezamiyyət sayı", secondary_y=True)
                            fig.update_layout(title_text="Aylıq Ezamiyyət Trendləri")
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Həftəlik aktivlik
                        if 'Tarix' in df.columns:
                            df['Həftənin günü'] = df['Tarix'].dt.day_name()
                            weekday_stats = df['Həftənin günü'].value_counts()
                            
                            fig = px.bar(
                                x=weekday_stats.index,
                                y=weekday_stats.values,
                                title="Həftəlik Ezamiyyət Paylanması",
                                color=weekday_stats.values,
                                color_continuous_scale='Viridis'
                            )
                            st.plotly_chart(fig, use_container_width=True)

                elif analysis_type == "Şöbə Analizi":
                    st.markdown("#### 🏢 Şöbə əsaslı Analiz")
                    
                    if 'Şöbə' in df.columns:
                        dept_stats = df.groupby('Şöbə').agg({
                            'Ümumi məbləğ': ['sum', 'mean', 'count'],
                            'Günlər': 'mean'
                        }).round(2)
                        
                        dept_stats.columns = ['Ümumi Xərc', 'Orta Xərc', 'Ezamiyyət Sayı', 'Orta Müddət']
                        dept_stats = dept_stats.sort_values('Ümumi Xərc', ascending=False)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Top 10 xərc edən şöbə
                            top_depts = dept_stats.head(10)
                            fig = px.bar(
                                x=top_depts['Ümumi Xərc'],
                                y=top_depts.index,
                                orientation='h',
                                title="Top 10 Xərc Edən Şöbə",
                                color=top_depts['Ümumi Xərc'],
                                color_continuous_scale='Reds'
                            )
                            fig.update_layout(yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Şöbə effektivliyi (xərc/ezamiyyət)
                            dept_stats['Effektivlik'] = dept_stats['Ümumi Xərc'] / dept_stats['Ezamiyyət Sayı']
                            efficiency = dept_stats.sort_values('Effektivlik', ascending=False).head(10)
                            
                            fig = px.scatter(
                                x=efficiency['Ezamiyyət Sayı'],
                                y=efficiency['Orta Xərc'],
                                size=efficiency['Ümumi Xərc'],
                                hover_name=efficiency.index,
                                title="Şöbə Effektivliyi",
                                labels={'x': 'Ezamiyyət Sayı', 'y': 'Orta Xərc'}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Detallı cədvəl
                        st.markdown("#### 📋 Şöbə Statistikaları")
                        st.dataframe(
                            dept_stats.style.format({
                                'Ümumi Xərc': '{:.2f} AZN',
                                'Orta Xərc': '{:.2f} AZN',
                                'Orta Müddət': '{:.1f} gün'
                            }),
                            use_container_width=True
                        )

                elif analysis_type == "Coğrafi Analiz":
                    st.markdown("#### 🌍 Coğrafi Paylanma")
                    
                    if 'Marşrut' in df.columns:
                        # Marşrut statistikaları
                        routes = df['Marşrut'].value_counts().head(15)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig = px.bar(
                                x=routes.values,
                                y=routes.index,
                                orientation='h',
                                title="Ən Populyar Marşrutlar",
                                color=routes.values,
                                color_continuous_scale='Blues'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Ölkə və şəhər analizi
                            if 'Ezamiyyət növü' in df.columns:
                                geo_stats = df.groupby(['Ezamiyyət növü', 'Marşrut'])['Ümumi məbləğ'].sum().reset_index()
                                
                                fig = px.treemap(
                                    geo_stats,
                                    path=['Ezamiyyət növü', 'Marşrut'],
                                    values='Ümumi məbləğ',
                                    title="Coğrafi Xərc Paylanması"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                elif analysis_type == "Maliyyə Analizi":
                    st.markdown("#### 💰 Maliyyə Performansı")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Xərc paylanması
                        if 'Ödəniş növü' in df.columns:
                            payment_dist = df.groupby('Ödəniş növü')['Ümumi məbləğ'].sum()
                            fig = px.pie(
                                values=payment_dist.values,
                                names=payment_dist.index,
                                title="Ödəniş Növləri üzrə Xərc",
                                hole=0.4
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Günlük müavinət vs bilet qiyməti
                        if 'Günlük müavinət' in df.columns and 'Bilet qiyməti' in df.columns:
                            fig = px.scatter(
                                df,
                                x='Günlük müavinət',
                                y='Bilet qiyməti',
                                size='Ümumi məbləğ',
                                title="Müavinət vs Bilet Qiyməti",
                                hover_data=['Marşrut'] if 'Marşrut' in df.columns else None
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col3:
                        # Xərc intervalları
                        expense_bins = [0, 500, 1000, 2000, 5000, float('inf')]
                        expense_labels = ['0-500', '500-1000', '1000-2000', '2000-5000', '5000+']
                        df['Xərc Kateqoriyası'] = pd.cut(df['Ümumi məbləğ'], bins=expense_bins, labels=expense_labels)
                        
                        expense_dist = df['Xərc Kateqoriyası'].value_counts()
                        fig = px.bar(
                            x=expense_dist.index,
                            y=expense_dist.values,
                            title="Xərc Kateqoriya Paylanması",
                            color=expense_dist.values
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Maliyyə cədvəli
                    st.markdown("#### 📊 Maliyyə Xülasəsi")
                    financial_summary = {
                        "Metrika": [
                            "Ümumi Xərc",
                            "Orta Xərc",
                            "Median Xərc",
                            "Maksimum Xərc",
                            "Minimum Xərc",
                            "Standart Sapma"
                        ],
                        "Dəyər": [
                            f"{df['Ümumi məbləğ'].sum():.2f} AZN",
                            f"{df['Ümumi məbləğ'].mean():.2f} AZN",
                            f"{df['Ümumi məbləğ'].median():.2f} AZN",
                            f"{df['Ümumi məbləğ'].max():.2f} AZN",
                            f"{df['Ümumi məbləğ'].min():.2f} AZN",
                            f"{df['Ümumi məbləğ'].std():.2f} AZN"
                        ]
                    }
                    st.table(pd.DataFrame(financial_summary))

                elif analysis_type == "Məqsəd Analizi":
                    st.markdown("#### 🎯 Ezamiyyət Məqsədləri")
                    
                    if 'Məqsəd' in df.columns:
                        purpose_stats = df.groupby('Məqsəd').agg({
                            'Ümumi məbləğ': ['sum', 'mean', 'count'],
                            'Günlər': 'mean'
                        }).round(2)
                        
                        purpose_stats.columns = ['Ümumi Xərc', 'Orta Xərc', 'Sayı', 'Orta Müddət']
                        purpose_stats = purpose_stats.sort_values('Ümumi Xərc', ascending=False)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Məqsəd paylanması
                            fig = px.bar(
                                x=purpose_stats.index,
                                y=purpose_stats['Ümumi Xərc'],
                                title="Məqsəd üzrə Xərclər",
                                color=purpose_stats['Ümumi Xərc']
                            )
                            fig.update_xaxes(tickangle=45)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Məqsəd effektivliyi
                            fig = px.scatter(
                                x=purpose_stats['Sayı'],
                                y=purpose_stats['Orta Xərc'],
                                size=purpose_stats['Ümumi Xərc'],
                                hover_name=purpose_stats.index,
                                title="Məqsəd Effektivliyi"
                            )
                            st.plotly_chart(fig, use_container_width=True)

                # Hesabat ixracı
                st.markdown("#### 📄 Hesabat İxracı")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Excel Hesabatı"):
                        with pd.ExcelWriter("analitik_hesabat.xlsx", engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Ham Məlumatlar', index=False)
                            
                            if 'Şöbə' in df.columns:
                                dept_stats = df.groupby('Şöbə').agg({
                                    'Ümumi məbləğ': ['sum', 'mean', 'count']
                                }).round(2)
                                dept_stats.to_excel(writer, sheet_name='Şöbə Statistikaları')
                            
                            if 'Marşrut' in df.columns:
                                route_stats = df['Marşrut'].value_counts()
                                route_stats.to_excel(writer, sheet_name='Marşrut Statistikaları')
                        
                        st.success("✅ Excel hesabatı yaradıldı!")
                
                with col2:
                    if st.button("📈 PDF Hesabatı"):
                        st.info("📄 PDF hesabat funksionallığı əlavə ediləcək")
                
                with col3:
                    if st.button("📧 Email Göndər"):
                        st.info("📨 Email göndərmə funksionallığı əlavə ediləcək")

            else:
                st.warning("📊 Analiz üçün məlumat yoxdur")
                
        except Exception as e:
            st.error(f"❌ Analitika xətası: {str(e)}")

        # 4. İDXAL/İXRAC TAB
        with admin_tabs[3]:
            st.markdown("### 📥 Məlumat İdxal/İxrac Mərkəzi")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📤 İxrac Seçimləri")
                
                try:
                    df = load_trip_data()
                    
                    if not df.empty:
                        # İxrac formatları
                        export_format = st.selectbox(
                            "Fayl formatı",
                            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"]
                        )
                        
                        # Tarix aralığı
                        col_a, col_b = st.columns(2)
                        with col_a:
                            start_date = st.date_input("Başlanğıc tarixi", value=datetime.now() - timedelta(days=30))
                        with col_b:
                            end_date = st.date_input("Bitmə tarixi", value=datetime.now())
                        
                        # Sütun seçimi
                        all_columns = df.columns.tolist()
                        selected_cols = st.multiselect(
                            "İxrac ediləcək sütunlar",
                            all_columns,
                            default=all_columns
                        )
                        
                        if st.button("📤 İxrac Et", type="primary"):
                            try:
                                # Tarix filtri tətbiq et
                                if 'Tarix' in df.columns:
                                    df['Tarix'] = pd.to_datetime(df['Tarix'], errors='coerce')
                                    mask = (df['Tarix'].dt.date >= start_date) & (df['Tarix'].dt.date <= end_date)
                                    export_df = df[mask][selected_cols]
                                else:
                                    export_df = df[selected_cols]
                                
                                filename = f"ezamiyyet_ixrac_{datetime.now().strftime('%Y%m%d_%H%M')}"
                                
                                if export_format == "Excel (.xlsx)":
                                    buffer = BytesIO()
                                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                        export_df.to_excel(writer, index=False, sheet_name='Ezamiyyətlər')
                                    
                                    st.download_button(
                                        "⬇️ Excel Faylını Yüklə",
                                        data=buffer.getvalue(),
                                        file_name=f"{filename}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                
                                elif export_format == "CSV (.csv)":
                                    csv = export_df.to_csv(index=False).encode('utf-8')
                                    st.download_button(
                                        "⬇️ CSV Faylını Yüklə",
                                        data=csv,
                                        file_name=f"{filename}.csv",
                                        mime="text/csv"
                                    )
                                
                                elif export_format == "JSON (.json)":
                                    json_str = export_df.to_json(orient='records', date_format='iso')
                                    st.download_button(
                                        "⬇️ JSON Faylını Yüklə",
                                        data=json_str,
                                        file_name=f"{filename}.json",
                                        mime="application/json"
                                    )
                                
                                st.success(f"✅ {len(export_df)} qeyd ixrac edildi!")
                                
                            except Exception as e:
                                st.error(f"❌ İxrac xətası: {str(e)}")
                    
                    else:
                        st.info("📝 İxrac üçün məlumat yoxdur")
                
                except Exception as e:
                    st.error(f"❌ İxrac xətası: {str(e)}")
            
            with col2:
                st.markdown("#### 📥 İdxal Seçimləri")
                
                uploaded_file = st.file_uploader(
                    "Fayl seçin",
                    type=['xlsx', 'csv', 'json'],
                    help="Excel, CSV və ya JSON formatında faylları idxal edə bilərsiniz"
                )
                
                if uploaded_file is not None:
                    try:
                        # Fayl növünü müəyyən et
                        file_extension = uploaded_file.name.split('.')[-1].lower()
                        
                        if file_extension == 'xlsx':
                            new_df = pd.read_excel(uploaded_file)
                        elif file_extension == 'csv':
                            new_df = pd.read_csv(uploaded_file)
                        elif file_extension == 'json':
                            new_df = pd.read_json(uploaded_file)
                        
                        st.markdown("#### 👀 İdxal Əvvəli Nəzər")
                        st.dataframe(new_df.head(), use_container_width=True)
                        
                        st.info(f"📊 {len(new_df)} qeyd tapıldı, {len(new_df.columns)} sütun")
                        
                        # İdxal seçimləri
                        import_mode = st.radio(
                            "İdxal rejimi",
                            ["Əlavə et", "Əvəzlə", "Birləşdir"]
                        )
                        
                        if st.button("📥 İdxal Et", type="primary"):
                            try:
                                existing_df = load_trip_data()
                                
                                if import_mode == "Əlavə et":
                                    if not existing_df.empty:
                                        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                                    else:
                                        combined_df = new_df
                                
                                elif import_mode == "Əvəzlə":
                                    combined_df = new_df
                                
                                elif import_mode == "Birləşdir":
                                    if not existing_df.empty:
                                        # Ümumi sütunları tap
                                        common_cols = list(set(existing_df.columns) & set(new_df.columns))
                                        if common_cols:
                                            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                                            combined_df = combined_df.drop_duplicates(subset=common_cols, keep='last')
                                        else:
                                            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                                    else:
                                        combined_df = new_df
                                
                                # Yeni məlumatları saxla
                                combined_df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                
                                st.success(f"✅ {len(new_df)} qeyd uğurla idxal edildi!")
                                st.info("🔄 Dəyişikliklərin görünməsi üçün səhifəni yeniləyin")
                                
                            except Exception as e:
                                st.error(f"❌ İdxal xətası: {str(e)}")
                    
                    except Exception as e:
                        st.error(f"❌ Fayl oxuma xətası: {str(e)}")

        # 5. SİSTEM PARAMETRLƏRİ TAB
        with admin_tabs[4]:
            st.markdown("### ⚙️ Sistem Konfiqurasiyası")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎨 İnterfeys Parametrləri")
                
                # Tema seçimi
                theme_color = st.selectbox(
                    "Tema rəngi",
                    ["Mavi", "Yaşıl", "Qırmızı", "Bənövşəyi"]
                )
                
                # Dil seçimi
                language = st.selectbox(
                    "Sistem dili",
                    ["Azərbaycan", "English", "Русский"]
                )
                
                # Valyuta
                currency = st.selectbox(
                    "Valyuta",
                    ["AZN", "USD", "EUR"]
                )
                
                # Tarix formatı
                date_format = st.selectbox(
                    "Tarix formatı",
                    ["DD.MM.YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]
                )
            
            with col2:
                st.markdown("#### 📊 Məlumat Parametrləri")
                
                # Səhifə başına qeyd sayı
                records_per_page = st.number_input(
                    "Səhifə başına qeyd sayı",
                    min_value=10,
                    max_value=100,
                    value=20
                )
                
                # Avtomatik backup
                auto_backup = st.checkbox("Avtomatik backup", value=True)
                
                if auto_backup:
                    backup_frequency = st.selectbox(
                        "Backup tezliyi",
                        ["Gündəlik", "Həftəlik", "Aylıq"]
                    )
                
                # Məlumat saxlama müddəti
                data_retention = st.number_input(
                    "Məlumat saxlama müddəti (ay)",
                    min_value=6,
                    max_value=120,
                    value=24
                )
            
            st.markdown("#### 🔔 Bildiriş Parametrləri")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                email_notifications = st.checkbox("Email bildirişləri", value=True)
                if email_notifications:
                    admin_email = st.text_input("Admin email", value="admin@company.com")
            
            with col2:
                sms_notifications = st.checkbox("SMS bildirişləri")
                if sms_notifications:
                    admin_phone = st.text_input("Admin telefon", value="+994xxxxxxxxx")
            
            with col3:
                system_notifications = st.checkbox("Sistem bildirişləri", value=True)
            
            # Parametrləri saxla
            if st.button("💾 Parametrləri Saxla", type="primary"):
                try:
                    config = {
                        "theme_color": theme_color,
                        "language": language,
                        "currency": currency,
                        "date_format": date_format,
                        "records_per_page": records_per_page,
                        "auto_backup": auto_backup,
                        "backup_frequency": backup_frequency if auto_backup else None,
                        "data_retention": data_retention,
                        "email_notifications": email_notifications,
                        "admin_email": admin_email if email_notifications else None,
                        "sms_notifications": sms_notifications,
                        "admin_phone": admin_phone if sms_notifications else None,
                        "system_notifications": system_notifications,
                        "last_updated": datetime.now().isoformat()
                    }
                    
                    with open("system_config.json", "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    
                    st.success("✅ Sistem parametrləri saxlanıldı!")
                    
                except Exception as e:
                    st.error(f"❌ Parametr saxlama xətası: {str(e)}")

        # 6. İSTİFADƏÇİ İDARƏETMƏSİ TAB
        with admin_tabs[5]:
            st.markdown("### 👥 İstifadəçi İdarəetməsi")
            
            # Mevcut istifadəçi statistikaları
            try:
                df = load_trip_data()
                
                if not df.empty and 'Ad' in df.columns:
                    user_stats = df.groupby(['Ad', 'Soyad']).agg({
                        'Ümumi məbləğ': ['sum', 'count', 'mean'],
                        'Tarix': 'max'
                    }).round(2) if 'Tarix' in df.columns else df.groupby(['Ad', 'Soyad']).agg({
                        'Ümumi məbləğ': ['sum', 'count', 'mean']
                    }).round(2)
                    
                    user_stats.columns = ['Ümumi Xərc', 'Ezamiyyət Sayı', 'Orta Xərc'] + (['Son Ezamiyyət'] if 'Tarix' in df.columns else [])
                    user_stats = user_stats.sort_values('Ümumi Xərc', ascending=False)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("#### 📊 İstifadəçi Statistikaları")
                        st.dataframe(
                            user_stats.style.format({
                                'Ümumi Xərc': '{:.2f} AZN',
                                'Orta Xərc': '{:.2f} AZN'
                            }),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown("#### 📈 Top İstifadəçilər")
                        top_users = user_stats.head(10)
                        fig = px.bar(
                            x=top_users['Ümumi Xərc'],
                            y=[f"{idx[0]} {idx[1]}" for idx in top_users.index],
                            orientation='h',
                            title="Ən Çox Xərc Edən İstifadəçilər"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.info("👤 Hələ qeydiyyatlı istifadəçi yoxdur")
                    
            except Exception as e:
                st.error(f"❌ İstifadəçi statistikaları xətası: {str(e)}")
            
            # İstifadəçi idarəetmə alətləri
            st.markdown("#### 🔧 İstifadəçi Alətləri")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Bildiriş Göndər"):
                    st.info("📨 Kütləvi bildiriş funksionallığı əlavə ediləcək")
            
            with col2:
                if st.button("📊 Həftəlik Hesabat"):
                    st.info("📈 Avtomatik hesabat funksionallığı əlavə ediləcək")
            
            with col3:
                if st.button("🔄 Məlumat Sinxronizasiyası"):
                    st.info("🔗 Xarici sistemlərlə sinxronizasiya əlavə ediləcək")

        # 7. SİSTEM ALƏTLƏRİ TAB
        with admin_tabs[6]:
            st.markdown("### 🔧 Sistem Təmizlik və Bərpa Alətləri")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🧹 Məlumat Təmizliyi")
                
                # Dublikat təmizliyi
                if st.button("🔍 Dublikatları Tap"):
                    try:
                        df = load_trip_data()
                        if not df.empty:
                            duplicates = df.duplicated().sum()
                            st.info(f"📊 {duplicates} dublikat qeyd tapıldı")
                            
                            if duplicates > 0:
                                if st.button("🗑️ Dublikatları Sil"):
                                    df_clean = df.drop_duplicates()
                                    df_clean.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                    st.success(f"✅ {duplicates} dublikat qeyd silindi!")
                        else:
                            st.info("📝 Təmizləmək üçün məlumat yoxdur")
                    except Exception as e:
                        st.error(f"❌ Dublikat axtarışı xətası: {str(e)}")
                
                # Boş sahə təmizliyi
                if st.button("🔍 Boş Sahələri Tap"):
                    try:
                        df = load_trip_data()
                        if not df.empty:
                            null_counts = df.isnull().sum()
                            null_counts = null_counts[null_counts > 0]
                            
                            if len(null_counts) > 0:
                                st.write("📊 Boş sahələr:")
                                for col, count in null_counts.items():
                                    st.write(f"- {col}: {count} boş qeyd")
                            else:
                                st.success("✅ Boş sahə tapılmadı")
                        else:
                            st.info("📝 Yoxlamaq üçün məlumat yoxdur")
                    except Exception as e:
                        st.error(f"❌ Boş sahə yoxlama xətası: {str(e)}")
            
            with col2:
                st.markdown("#### 💾 Backup və Bərpa")
                
                # Manuel backup
                if st.button("💾 Manuel Backup Yarat"):
                    try:
                        df = load_trip_data()
                        if not df.empty:
                            backup_filename = f"backup_ezamiyyet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                            df.to_excel(backup_filename, index=False)
                            st.success(f"✅ Backup yaradıldı: {backup_filename}")
                        else:
                            st.warning("📝 Backup üçün məlumat yoxdur")
                    except Exception as e:
                        st.error(f"❌ Backup xətası: {str(e)}")
                
                # Sistem məlumatları
                if st.button("ℹ️ Sistem Məlumatları"):
                    try:
                        df = load_trip_data()
                        file_size = os.path.getsize("ezamiyyet_melumatlari.xlsx") if os.path.exists("ezamiyyet_melumatlari.xlsx") else 0
                        
                        system_info = {
                            "Cədvəl ölçüsü": f"{file_size / 1024:.2f} KB",
                            "Qeyd sayı": len(df) if not df.empty else 0,
                            "Sütun sayı": len(df.columns) if not df.empty else 0,
                            "Son yeniləmə": datetime.now().strftime("%d.%m.%Y %H:%M")
                        }
                        
                        for key, value in system_info.items():
                            st.metric(key, value)
                            
                    except Exception as e:
                        st.error(f"❌ Sistem məlumatları xətası: {str(e)}")
            
            # Sistem logları
            st.markdown("#### 📜 Sistem Logları")
            
            # Bu hissə gələcəkdə log sisteminin əlavə edilməsi üçün hazırdır
            if st.checkbox("Debug rejimi"):
                st.code("""
                Sistem Debug Məlumatları:
                - Session State: OK
                - Fayl Əlçatanlığı: OK  
                - Admin Sessiyası: Aktiv
                - Son Aktivlik: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
                """)
            
            # Kritik əməliyyatlar
            st.markdown("#### ⚠️ Kritik Əməliyyatlar")
            st.warning("🚨 Bu əməliyyatlar geri qaytarıla bilməz!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Bütün Məlumatları Sil", type="secondary"):
                    if st.checkbox("⚠️ Bütün məlumatların silinəcəyini başa düşürəm"):
                        if st.text_input("Təsdiq üçün 'SİL' yazın") == "SİL":
                            try:
                                empty_df = pd.DataFrame()
                                empty_df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                                st.success("✅ Bütün məlumatlar silindi!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Silinmə xətası: {str(e)}")
            
            with col2:
                if st.button("🔄 Sistemi Sıfırla", type="secondary"):
                    if st.checkbox("⚠️ Sistem sıfırlanacağını başa düşürəm"):
                        if st.text_input("Təsdiq üçün 'RESET' yazın") == "RESET":
                            try:
                                # Session state-i təmizlə
                                for key in list(st.session_state.keys()):
                                    del st.session_state[key]
                                st.success("✅ Sistem sıfırlandı!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Sıfırlama xətası: {str(e)}")

# Admin panel kodunun sonuna əlavə edilməsi gereken hissələr

                # Ana admin panel tab-larının sonuna əlavə kod
                
                # Sessiya izləmə
        # Footer məlumatları
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption(f"🔐 Admin Sessiyası: {st.session_state.admin_session_time.strftime('%H:%M:%S')}")
        
        with col2:
            try:
                df = load_trip_data()
                st.caption(f"📊 Cəmi məlumat: {len(df)} qeyd")
            except:
                st.caption("📊 Cəmi məlumat: 0 qeyd")
        
        with col3:
            st.caption(f"📅 Son yeniləmə: {datetime.now().strftime('%d.%m.%Y %H:%M')}")


# Admin panel kodunun bitişi
        else:
            st.warning("🔐 Admin paneli üçün giriş tələb olunur")
