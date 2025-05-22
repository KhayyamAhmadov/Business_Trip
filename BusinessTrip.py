import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from io import BytesIO

# Səhifə konfiqurasiyası
st.set_page_config(
    page_title="Ezamiyyət Hesablayıcı", 
    page_icon="✈️",
    layout="wide"
)

# CSS stilləri
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: #1a237e;
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-header {
        background: #283593;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        font-size: 1.1rem;
    }
    .stSelectbox > div > div {border-radius: 8px!important;}
    .stDateInput > div > div {border-radius: 8px!important;}
    .stRadio > div {gap: 1rem;}
</style>
""", unsafe_allow_html=True)

# Sabitlər
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
    "Lerik", "Masallı", "Mingəçevir", "Naftalan", "Neftçala", "Naxçıvan", "Oğuz",
    "Ordubad (Naxçıvan MR)", "Qəbələ", "Qax", "Qazax", "Qobustan", "Quba", "Qubadlı",
    "Qusar", "Saatlı", "Sabirabad", "Sədərək (Naxçıvan MR)", "Salyan", "Samux", "Şabran",
    "Şahbuz (Naxçıvan MR)", "Şamaxı", "Şəki", "Şəmkir", "Şərur (Naxçıvan MR)", "Şirvan",
    "Şuşa", "Sumqayıt", "Tərtər", "Tovuz", "Ucar", "Yardımlı", "Yevlax", "Zaqatala",
    "Zəngilan", "Zərdab"
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
    ("Bakı", "Gəncə"): 100,
    ("Bakı", "Şəki"): 90,
    ("Bakı", "Lənkəran"): 80,
    ("Bakı", "Sumqayıt"): 50,
    ("Bakı", "Mingəçevir"): 85,
    ("Bakı", "Şirvan"): 75,
    ("Bakı", "Naxçıvan"): 120,
    ("Gəncə", "Şəki"): 70,
    ("Gəncə", "Tovuz"): 60,
}

PAYMENT_TYPES = {
    "Ödənişsiz": 0,
    "10% ödəniş edilməklə": 0.1,
    "Tam ödəniş edilməklə": 1
}

# Funksiyalar
def calculate_domestic_amount(from_city, to_city):
    return DOMESTIC_ROUTES.get((from_city, to_city)) or DOMESTIC_ROUTES.get((to_city, from_city)) or 70

def calculate_days(start_date, end_date):
    return (end_date - start_date).days + 1

def calculate_total_amount(daily_allowance, days, payment_type):
    return daily_allowance * days * PAYMENT_TYPES[payment_type]

def save_trip_data(data):
    df_new = pd.DataFrame([data])
    try:
        df_existing = pd.read_csv("ezamiyyet_melumatlari.csv")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    except FileNotFoundError:
        df_combined = df_new
    df_combined.to_csv("ezamiyyet_melumatlari.csv", index=False)
    return df_combined

def load_trip_data():
    try:
        df = pd.read_csv("ezamiyyet_melumatlari.csv")
        # Köhnə versiyalar üçün zəruri sütunları yoxla
        required_columns = {
            'Tarix': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Günlər': 0,
            'Ümumi məbləğ': 0,
            'Ödəniş növü': 'Tam ödəniş edilməklə'
        }
        
        for col, default_val in required_columns.items():
            if col not in df.columns:
                df[col] = default_val
                
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# Əsas interfeys
st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət Hesablayıcı</h1><p>Azərbaycan Respublikası Dövlət Statistika Komitəsi</p></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Yeni Ezamiyyət", "🔒 Admin Panel"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header">👤 Şəxsi Məlumatlar</div>', unsafe_allow_html=True)
        first_name = st.text_input("Ad")
        last_name = st.text_input("Soyad")
        father_name = st.text_input("Ata adı")
        position = st.text_input("Vəzifə")
        
        st.markdown('<div class="section-header">🏢 Təşkilat Məlumatları</div>', unsafe_allow_html=True)
        department = st.selectbox("Şöbə", DEPARTMENTS)
        
        st.markdown('<div class="section-header">🧳 Ezamiyyət Məlumatları</div>', unsafe_allow_html=True)
        trip_type = st.radio("Ezamiyyət növü", ["Ölkə daxili", "Ölkə xarici"])
        payment_type = st.selectbox("Ödəniş növü", list(PAYMENT_TYPES.keys()))
        
        if trip_type == "Ölkə daxili":
            col_route1, col_route2 = st.columns(2)
            with col_route1:
                from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"))
            with col_route2:
                to_city = st.selectbox("Haraya", [c for c in CITIES if c != from_city])
            daily_allowance = calculate_domestic_amount(from_city, to_city)
        else:
            country = st.selectbox("Ölkə", list(COUNTRIES.keys()))
            daily_allowance = COUNTRIES[country]
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("Başlanğıc tarixi")
        with col_date2:
            end_date = st.date_input("Bitmə tarixi")
        
        purpose = st.text_area("Ezamiyyət məqsədi")

    with col2:
        st.markdown('<div class="section-header">💰 Hesablama</div>', unsafe_allow_html=True)
        if start_date and end_date and end_date >= start_date:
            trip_days = calculate_days(start_date, end_date)
            total_amount = calculate_total_amount(daily_allowance, trip_days, payment_type)
            
            st.metric("Günlük məbləğ", f"{daily_allowance} AZN")
            st.metric("Gün sayı", trip_days)
            st.metric("Ümumi məbləğ", f"{total_amount:.2f} AZN")
            
            if payment_type != "Tam ödəniş edilməklə":
                original = daily_allowance * trip_days
                st.metric("Tam məbləğ", f"{original} AZN", delta=f"-{original - total_amount} AZN")

        if st.button("💾 Yadda Saxla", type="primary"):
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
                "Başlanğıc tarixi": start_date.strftime("%Y-%m-%d"),
                "Bitmə tarixi": end_date.strftime("%Y-%m-%d"),
                "Günlər": trip_days,
                "Günlük məbləğ": daily_allowance,
                "Ümumi məbləğ": total_amount,
                "Məqsəd": purpose
            }
            save_trip_data(trip_data)
            st.success("Məlumatlar yadda saxlanıldı!")
            st.balloons()

with tab2:
    st.markdown('<div class="section-header">🔒 Admin Girişi</div>', unsafe_allow_html=True)
    admin_user = st.text_input("İstifadəçi adı")
    admin_pass = st.text_input("Şifrə", type="password")
    
    if st.button("Giriş et"):
        if admin_user == "admin" and admin_pass == "admin123":
            st.session_state.admin_logged = True
    
    if st.session_state.get('admin_logged'):
        st.markdown('<div class="section-header">📊 Statistika Paneli</div>', unsafe_allow_html=True)
        df = load_trip_data()
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ümumi Ezamiyyət", len(df))
            with col2:
                st.metric("Ümumi Xərc", f"{df.get('Ümumi məbləğ', pd.Series([0]*len(df))).sum():.2f} AZN")
            with col3:
                days_data = df.get('Günlər', pd.Series([0]*len(df)))
                avg_days = days_data.mean() if not days_data.empty else 0
                st.metric("Orta Müddət", f"{avg_days:.1f} gün")
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                fig = px.pie(df, names='Ezamiyyət növü', title='Ezamiyyət Növləri')
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                fig = px.bar(df, x='Şöbə', y='Ümumi məbləğ', title='Şöbələr üzrə Xərclər')
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="section-header">📤 İxrac Funksiyaları</div>', unsafe_allow_html=True)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Ezamiyyətlər')
                
                summary = pd.DataFrame({
                    'Göstərici': ['Ümumi Ezamiyyət', 'Ümumi Xərc', 'Orta Müddət'],
                    'Dəyər': [len(df), df.get('Ümumi məbləğ', 0).sum(), df.get('Günlər', 0).mean()]
                })
                summary.to_excel(writer, index=False, sheet_name='Statistika')
            
            st.download_button(
                label="📥 Excel Faylını Yüklə",
                data=output.getvalue(),
                file_name=f"ezamiyyet_statistika_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown('<div class="section-header">🗑️ Məlumatların Idarə Edilməsi</div>', unsafe_allow_html=True)
            selected = st.multiselect("Silinəcək qeydlər", df.index)
            if st.button("Seçilmişləri sil"):
                df = df.drop(selected)
                df.to_csv("ezamiyyet_melumatlari.csv", index=False)
                st.success(f"{len(selected)} qeyd silindi!")
                st.experimental_rerun()
        else:
            st.warning("Hələ heç bir məlumat yoxdur")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; margin-top: 2rem;'>"
    "© 2024 Dövlət Statistika Komitəsi | Versiya 2.2"
    "</div>", 
    unsafe_allow_html=True
)
