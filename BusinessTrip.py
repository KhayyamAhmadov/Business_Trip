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
            df = pd.read_excel("ezamiyyet_melumatlari.xlsx")
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
                        "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                        "Başlanğıc tarixi": start_date.strftime("%Y-%m-%d"),
                        "Bitmə tarixi": end_date.strftime("%Y-%m-%d"),
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

# 1. DASHBOARD TAB
with admin_tabs[0]:
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Tarixi sütunları düzəlt
            if 'Tarix' in df.columns:
                df['Tarix'] = pd.to_datetime(df['Tarix'], errors='coerce')
            if 'Başlanğıc tarixi' in df.columns:
                df['Başlanğıc tarixi'] = pd.to_datetime(df['Başlanğıc tarixi'], errors='coerce')
            
            # Rəqəmsal sütunları düzəlt
            numeric_cols = ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Əsas metrikalar
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                # Interaktiv tarix seçimi ilə trend analizi
                st.markdown("### 📈 Xərclərin Zaman üzrə Dəyişimi")
                
                date_col = 'Başlanğıc tarixi' if 'Başlanğıc tarixi' in df.columns else 'Tarix'
                df[date_col] = pd.to_datetime(df[date_col])
                
                # Tarix aralığı seçimi
                min_date = df[date_col].min().date()
                max_date = df[date_col].max().date()
                selected_dates = st.date_input(
                    "Tarix aralığını seçin",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

                
                # Filtrə görə məlumat
                filtered_df = df[
                    (df[date_col].dt.date >= selected_dates[0]) & 
                    (df[date_col].dt.date <= selected_dates[1])
                ]
                
                # Xərc trendləri
                weekly_data = filtered_df.set_index(date_col).resample('W')['Ümumi məbləğ'].sum().reset_index()
                fig = px.line(
                    weekly_data,
                    x=date_col,
                    y='Ümumi məbləğ',
                    title='Həftəlik Xərc Trendləri',
                    markers=True,
                    line_shape='spline',
                    template='plotly_white'
                )

                fig.update_traces(
                    line=dict(width=3, color='#6366f1'),
                    marker=dict(size=8, color='#8b5cf6')
                )
                fig.update_layout(
                    hoverlabel=dict(bgcolor="white", font_size=12),
                    xaxis_title='',
                    yaxis_title='Ümumi Xərc (AZN)'
                )
                st.plotly_chart(fig, use_container_width=True)

            
                # Rəqəmsal olmayan sütunları sil
                numeric_df = filtered_df.select_dtypes(include=['number'])
                if not numeric_df.empty:
                    weekly_data = numeric_df.resample('W', on=date_col).sum().reset_index()
                else:
                    st.warning("Hesablama üçün rəqəmsal məlumat yoxdur")


            with col2:
                # Şöbələr üzrə interaktiv treemap
                st.markdown("### 🌳 Şöbə Xərcləri")
                
                fig = px.treemap(
                    df,
                    path=['Şöbə'],
                    values='Ümumi məbləğ',
                    color='Ümumi məbləğ',
                    color_continuous_scale='Blues',
                    hover_data=['Ezamiyyət növü', 'Günlər']
                )
                fig.update_layout(
                    margin=dict(t=30, l=0, r=0, b=0),
                    height=500
                )
                fig.update_traces(
                    textinfo='label+value+percent parent',
                    texttemplate='<b>%{label}</b><br>%{value:.2f} AZN<br>(%{percentParent:.1%})'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Yeni interaktiv heatmap
            st.markdown("### 🔥 Aylıq Aktivlik Xəritəsi")
            
            heatmap_df = df.copy()
            heatmap_df['Ay'] = heatmap_df[date_col].dt.month_name()
            heatmap_df['Həftənin Günü'] = heatmap_df[date_col].dt.day_name()
            heatmap_df['Həftə'] = heatmap_df[date_col].dt.isocalendar().week
            
            fig = px.density_heatmap(
                heatmap_df,
                x='Həftənin Günü',
                y='Ay',
                z='Ümumi məbləğ',
                histfunc='sum',
                color_continuous_scale='YlGnBu',
                category_orders={
                    "Həftənin Günü": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "Ay": ["January", "February", "March", "April", "May", "June", 
                           "July", "August", "September", "October", "November", "December"]
                }
            )
            fig.update_layout(
                xaxis_title='',
                yaxis_title='',
                coloraxis_colorbar=dict(title='Ümumi Xərc')
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("📭 Hələ heç bir ezamiyyət qeydiyyatı yoxdur")
            
    except Exception as e:
        st.error(f"❌ Dashboard yüklənərkən xəta: {str(e)}")

# 2. ANALİTİKA TAB yeniləməsi
with admin_tabs[2]:
    st.markdown("### 📈 Detallı Analitika və Hesabatlar")
    
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Yeni interaktiv scatter matrix
            st.markdown("#### 🔍 Çoxölçülü Analiz")
            
            numeric_cols = ['Ümumi məbləğ', 'Günlər', 'Günlük müavinət', 'Bilet qiyməti']
            selected_cols = st.multiselect(
                "Analiz üçün sütunları seçin",
                numeric_cols,
                default=numeric_cols[:3]
            )
            
            if len(selected_cols) >= 2:
                fig = px.scatter_matrix(
                    df,
                    dimensions=selected_cols,
                    color='Ezamiyyət növü',
                    hover_name='Marşrut',
                    title='Parametr Arası Əlaqələr'
                )
                fig.update_traces(
                    diagonal_visible=False,
                    showupperhalf=False,
                    marker=dict(size=4, opacity=0.6)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Minimum 2 ədəd rəqəmsal sütun seçin")

            # Dinamik filtrlənə bilən box plot
            st.markdown("#### 📦 Xərc Paylanması")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                group_by = st.selectbox(
                    "Qruplaşdırma üçün sütun",
                    ['Ezamiyyət növü', 'Şöbə', 'Ödəniş növü']
                )
                log_scale = st.checkbox("Loqarifmik miqyas")
                
            with col2:
                fig = px.box(
                    df,
                    x=group_by,
                    y='Ümumi məbləğ',
                    color=group_by,
                    points="all",
                    hover_data=['Ad', 'Soyad'],
                    log_y=log_scale
                )
                fig.update_layout(
                    showlegend=False,
                    xaxis_title='',
                    yaxis_title='Ümumi Xərc (AZN)'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Dinamik map vizualizasiyası (əlavə məlumat tələb edir)
            st.markdown("#### 🌍 Coğrafi Xərc Xəritəsi")
            
            # Geokoordinatlar üçün nümunə məlumat (əlavə edilməlidir)
            geo_df = pd.DataFrame({
                'Şəhər': ['Bakı', 'Gəncə', 'Sumqayıt'],
                'Lat': [40.4093, 40.6828, 40.5897],
                'Lon': [49.8671, 46.3606, 49.6686],
                'Ümumi Xərc': [df[df['Marşrut'].str.contains(city)]['Ümumi məbləğ'].sum() 
                              for city in ['Bakı', 'Gəncə', 'Sumqayıt']]
            })
            
            fig = px.scatter_geo(
                geo_df,
                lat='Lat',
                lon='Lon',
                size='Ümumi Xərc',
                hover_name='Şəhər',
                projection='natural earth',
                title='Şəhərlər üzrə xərclər'
            )
            fig.update_geos(
                resolution=50,
                showcountries=True,
                countrycolor="Black"
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("📊 Analiz üçün məlumat yoxdur")
            
    except Exception as e:
        st.error(f"❌ Analitika xətası: {str(e)}")

# 2. MƏLUMAT İDARƏETMƏSİ TAB hissəsindəki kodu aşağıdakı kimi düzəldin:

with admin_tabs[1]:
    st.markdown("### 🗂️ Məlumatların İdarə Edilməsi")
    
    try:
        df = load_trip_data()
        
        if not df.empty:
            # Tarix sütunlarını avtomatik çevir
            date_columns = ['Tarix', 'Başlanğıc tarixi', 'Bitmə tarixi']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Filtr və axtarış seçimləri
            st.markdown("#### 🔍 Filtr və Axtarış")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_filter = st.selectbox(
                    "📅 Tarix filtri",
                    ["Hamısı", "Son 7 gün", "Son 30 gün", "Son 3 ay", "Bu il", "Seçilmiş aralıq"]
                )
                
                if date_filter == "Seçilmiş aralıq":
                    start_date = st.date_input("Başlanğıc tarixi")
                    end_date = st.date_input("Bitmə tarixi")
            
            with col2:
                if 'Şöbə' in df.columns:
                    departments = ["Hamısı"] + sorted(df['Şöbə'].unique().tolist())
                    selected_dept = st.selectbox("🏢 Şöbə filtri", departments)
            
            with col3:
                if 'Ezamiyyət növü' in df.columns:
                    trip_types = ["Hamısı"] + df['Ezamiyyət növü'].unique().tolist()
                    selected_type = st.selectbox("✈️ Ezamiyyət növü", trip_types)
            
            search_term = st.text_input("🔎 Ad və ya soyad üzrə axtarış")

            # Filtirləmə məntiqi
            filtered_df = df.copy()
            if date_filter != "Hamısı" and 'Tarix' in df.columns:
                if date_filter == "Seçilmiş aralıq":
                    filtered_df = filtered_df[
                        (filtered_df['Tarix'].dt.date >= start_date) & 
                        (filtered_df['Tarix'].dt.date <= end_date)
                    ]
                else:
                    now = datetime.now()
                    if date_filter == "Son 7 gün":
                        cutoff = now - timedelta(days=7)
                    elif date_filter == "Son 30 gün":
                        cutoff = now - timedelta(days=30)
                    elif date_filter == "Son 3 ay":
                        cutoff = now - timedelta(days=90)
                    elif date_filter == "Bu il":
                        cutoff = datetime(now.year, 1, 1)
                    filtered_df = filtered_df[filtered_df['Tarix'] >= cutoff]

            if selected_dept != "Hamısı" and 'Şöbə' in df.columns:
                filtered_df = filtered_df[filtered_df['Şöbə'] == selected_dept]

            if selected_type != "Hamısı" and 'Ezamiyyət növü' in df.columns:
                filtered_df = filtered_df[filtered_df['Ezamiyyət növü'] == selected_type]

            if search_term:
                mask = filtered_df['Ad'].str.contains(search_term, case=False, na=False) | filtered_df['Soyad'].str.contains(search_term, case=False, na=False)
                filtered_df = filtered_df[mask]

            # Nəticələr
            st.markdown(f"#### 📊 Nəticələr ({len(filtered_df)} qeyd)")
            
            if len(filtered_df) > 0:
                available_columns = filtered_df.columns.tolist()
                default_columns = [col for col in ['Ad', 'Soyad', 'Şöbə', 'Marşrut', 'Ümumi məbləğ', 'Başlanğıc tarixi'] if col in available_columns]
                
                selected_columns = st.multiselect(
                    "Göstəriləcək sütunları seçin",
                    available_columns,
                    default=default_columns
                )
                
                if selected_columns:
                    display_df = filtered_df[selected_columns].copy()
                    
                    # Sütun konfiqurasiyası
                    column_config = {}
                    for col in selected_columns:
                        if col in date_columns:
                            column_config[col] = st.column_config.DatetimeColumn(
                                col,
                                format="DD.MM.YYYY HH:mm" if col == 'Tarix' else "DD.MM.YYYY"
                            )
                        elif col in ['Ümumi məbləğ', 'Günlük müavinət', 'Bilet qiyməti']:
                            column_config[col] = st.column_config.NumberColumn(
                                col,
                                format="%.2f AZN"
                            )
                    
                    edited_df = st.data_editor(
                        display_df,
                        column_config=column_config,
                        use_container_width=True,
                        height=600,
                        key="admin_data_editor"
                    )
                    
                    # Dəyişiklikləri saxla
                    if st.button("💾 Dəyişiklikləri Saxla", type="primary"):
                        try:
                            # Tarix sütunlarını formatla
                            for col in date_columns:
                                if col in edited_df.columns:
                                    edited_df[col] = pd.to_datetime(edited_df[col], errors='coerce')
                            
                            # Əsas dataframe-i yenilə
                            df.update(edited_df)
                            
                            # Faylı saxla
                            df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                            st.success("✅ Dəyişikliklər saxlanıldı!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Saxlama xətası: {str(e)}")
                
                else:
                    st.warning("Zəhmət olmasa göstəriləcək sütunları seçin")
            
            else:
                st.info("🔍 Filtrə uyğun qeyd tapılmadı")
        
        else:
            st.warning("📭 Hələ heç bir məlumat yoxdur")
            
    except Exception as e:
        st.error(f"❌ Məlumat idarəetməsi xətası: {str(e)}")       
        
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
