import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO

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
    .login-box .stTextInput {
        width: 30%;
        margin: 0 auto;
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
def calculate_domestic_amount(from_city, to_city):
    return DOMESTIC_ROUTES.get((from_city, to_city)) or DOMESTIC_ROUTES.get((to_city, from_city)) or 70

def calculate_days(start_date, end_date):
    return (end_date - start_date).days + 1

def calculate_total_amount(daily_allowance, days, payment_type, ticket_price=0):
    return (daily_allowance * days + ticket_price) * PAYMENT_TYPES[payment_type]

def save_trip_data(data):
    try:
        df_new = pd.DataFrame([data])
        df_existing = pd.read_excel("ezamiyyet_melumatlari.xlsx")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    except FileNotFoundError:
        df_combined = df_new
    df_combined.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
    return df_combined

def load_trip_data():
    try:
        df = pd.read_excel("ezamiyyet_melumatlari.xlsx")
        required_columns = {
            'Tarix': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Günlər': 0,
            'Ümumi məbləğ': 0,
            'Ödəniş növü': 'Tam ödəniş edilməklə',
            'Marşrut': 'Təyin edilməyib',
            'Bilet qiyməti': 0,
            'Günlük müavinət': 70
        }
        for col, default in required_columns.items():
            if col not in df.columns:
                df[col] = default
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()

# ============================== ƏSAS İNTERFEYS ==============================
st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət İdarəetmə Sistemi</h1></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📋 Yeni Ezamiyyət", "🔐 Admin Paneli"])

# ============================== YENİ EZAMİYYƏT HISSESI ==============================
with tab1:
    with st.container():
        col1, col2 = st.columns([2, 1], gap="large")
        
        # Sol sütun
        with col1:
            with st.expander("👤 Şəxsi Məlumatlar", expanded=True):
                cols = st.columns(2)
                with cols[0]:
                    first_name = st.text_input("Ad", key="first_name")
                    father_name = st.text_input("Ata adı", key="father_name")
                with cols[1]:
                    last_name = st.text_input("Soyad", key="last_name")
                    position = st.text_input("Vəzifə", key="position")

            with st.expander("🏢 Təşkilat Məlumatları", expanded=True):
                department = st.selectbox("Şöbə", DEPARTMENTS, key="department")

            with st.expander("🧳 Ezamiyyət Detalları", expanded=True):
                trip_type = st.radio("Ezamiyyət növü", ["Ölkə daxili", "Ölkə xarici"], key="trip_type")
                payment_type = st.selectbox("Ödəniş növü", list(PAYMENT_TYPES.keys()), key="payment_type")

                if trip_type == "Ölkə daxili":
                    cols = st.columns(2)
                    with cols[0]:
                        from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"))
                    with cols[1]:
                        to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city])
                    ticket_price = calculate_domestic_amount(from_city, to_city)
                    daily_allowance = 70  # Sabit günlük müavinət
                else:
                    country = st.selectbox("Ölkə", list(COUNTRIES.keys()))
                    daily_allowance = COUNTRIES[country]
                    ticket_price = 0

                cols = st.columns(2)
                with cols[0]:
                    start_date = st.date_input("Başlanğıc tarixi")
                with cols[1]:
                    end_date = st.date_input("Bitmə tarixi")
                
                purpose = st.text_area("Ezamiyyət haqqında əlavə məlumat almaq üçün suallarınızı qeyd edin.", height=100)

        # Sağ sütun (Hesablama)
        with col2:
            with st.container():
                st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
                
                if start_date and end_date and end_date >= start_date:
                    trip_days = calculate_days(start_date, end_date)
                    total_amount = calculate_total_amount(daily_allowance, trip_days, payment_type, ticket_price)
                    
                    if trip_type == "Ölkə daxili":
                        st.metric("🚌 Bilet qiyməti", f"{ticket_price} AZN", 
                                 help="Seçilmiş marşrut üzrə nəqliyyat xərci")
                        st.metric("📅 Günlük müavinət", f"{daily_allowance} AZN", 
                                 help="Sabit günlük müavinət məbləği")
                    
                    st.metric("⏳ Ezamiyyət müddəti", f"{trip_days} gün")
                    st.metric("💳 Ümumi ödəniləcək məbləğ", f"{total_amount:.2f} AZN", 
                             delta="10% endirim" if payment_type == "10% ödəniş edilməklə" else None)

                if st.button("✅ Yadda Saxla", type="primary", use_container_width=True):
                    trip_data = {
                        "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Ad": first_name,
                        "Soyad": last_name,
                        "Ata adı": father_name,
                        "Vəzifə": position,
                        "Şöbə": department,
                        "Ezamiyyət növü": trip_type,
                        "Ödəniş növü": payment_type,
                        "Marşrut": f"{from_city} → {to_city}" if trip_type == "Ölkə daxili" else country,
                        "Bilet qiyməti": ticket_price,
                        "Günlük müavinət": daily_allowance,
                        "Başlanğıc tarixi": start_date.strftime("%Y-%m-%d"),
                        "Bitmə tarixi": end_date.strftime("%Y-%m-%d"),
                        "Günlər": trip_days,
                        "Ümumi məbləğ": total_amount,
                        "Məqsəd": purpose
                    }
                    save_trip_data(trip_data)
                    st.success("Məlumatlar uğurla yadda saxlanıldı!")

# ============================== ADMIN PANELI ==============================
with tab2:
    with st.container():
        st.markdown('<div class="section-header">🔐 Admin Girişi</div>', unsafe_allow_html=True)
        
        cols = st.columns(2)
        with cols[0]:
            admin_user = st.text_input("İstifadəçi adı", key="admin_user")
        with cols[1]:
            admin_pass = st.text_input("Şifrə", type="password", key="admin_pass")
        
        if st.button("🚪 Giriş et", key="admin_login"):
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.admin_logged = True
                st.rerun()
            else:
                st.error("Giriş məlumatları yanlışdır!")

        if st.session_state.get('admin_logged'):
            st.markdown('<div class="section-header">📊 İdarəetmə Paneli</div>', unsafe_allow_html=True)
            df = load_trip_data()
            
            if not df.empty:
                with st.expander("📋 Bütün Qeydlər", expanded=True):
                    st.dataframe(df, use_container_width=True, height=400)
                
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Ümumi Ezamiyyət", len(df))
                with cols[1]:
                    st.metric("Ümumi Xərc", f"{df['Ümumi məbləğ'].sum():.2f} AZN")
                with cols[2]:
                    st.metric("Orta Müddət", f"{df['Günlər'].mean():.1f} gün")
                
                with st.expander("📈 Statistika", expanded=True):
                    cols = st.columns(2)
                    with cols[0]:
                        fig = px.pie(df, names='Ezamiyyət növü', 
                                   title='Ezamiyyət Növlərinin Dağılımı',
                                   color_discrete_sequence=['#6366f1', '#8b5cf6'])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with cols[1]:
                        fig = px.bar(df.sort_values('Ümumi məbləğ', ascending=False).head(10), 
                                   x='Şöbə', y='Ümumi məbləğ', 
                                   title='Top 10 Xərc Edən Şöbə',
                                   color='Ümumi məbləğ',
                                   color_continuous_scale='Bluered')
                        st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("📤 İxrac Funksiyaları"):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Ezamiyyətlər')
                        st.download_button(
                            label="📥 Excel faylını yüklə",
                            data=output.getvalue(),
                            file_name="ezamiyyet_qeydleri.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with st.expander("🗑️ Qeyd Silmə", expanded=True):
                    selected = st.multiselect(
                        "Silinəcək qeydləri seçin:",
                        options=df.index,
                        format_func=lambda x: f"{df.iloc[x]['Ad']} {df.iloc[x]['Soyad']} | {df.iloc[x]['Marşrut']}"
                    )
                    if st.button("🔴 Seçilmişləri sil", type="primary"):
                        df = df.drop(selected)
                        df.to_excel("ezamiyyet_melumatlari.xlsx", index=False)
                        st.success(f"{len(selected)} qeyd silindi!")
                        st.rerun()
            else:
                st.warning("Hələ heç bir qeyd mövcud deyil")
