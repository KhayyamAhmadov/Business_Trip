import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Ezamiyyət Hesablayıcı", 
    page_icon="✈️",
    layout="wide"
)

# CSS stil düzenlemeleri
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sabitler
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

def calculate_domestic_amount(from_city, to_city):
    """Yerli ezamiyyət məbləğini hesablayır"""
    return DOMESTIC_ROUTES.get((from_city, to_city)) or DOMESTIC_ROUTES.get((to_city, from_city)) or 70

def calculate_days(start_date, end_date):
    """Tarixlər arası gün sayını hesablayır"""
    return (end_date - start_date).days + 1

def save_trip_data(data):
    """Məlumatları CSV faylına yadda saxlayır"""
    df_new = pd.DataFrame([data])
    
    try:
        df_existing = pd.read_csv("ezamiyyet_melumatlari.csv")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    except FileNotFoundError:
        df_combined = df_new
    
    df_combined.to_csv("ezamiyyet_melumatlari.csv", index=False)
    return df_combined

def load_trip_data():
    """CSV faylından məlumatları yükləyir"""
    try:
        df = pd.read_csv("ezamiyyet_melumatlari.csv")
        # Köhnə versiyalar üçün uyğunlaşdırma
        if 'Ümumi məbləğ' not in df.columns:
            df['Ümumi məbləğ'] = 0
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# Başlıq
st.markdown('<div class="main-header"><h1>✈️ Ezamiyyət Hesablayıcı</h1><p>Azərbaycan Respublikası Dövlət Statistika Komitəsi</p></div>', unsafe_allow_html=True)

# Tablar
tab1, tab2, tab3 = st.tabs(["📝 Yeni Ezamiyyət", "📊 Statistika", "🔒 Admin Panel"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header"><h3>👤 Şəxsi Məlumatlar</h3></div>', unsafe_allow_html=True)
        
        col_name1, col_name2 = st.columns(2)
        with col_name1:
            first_name = st.text_input("Ad", key="first_name")
            father_name = st.text_input("Ata adı", key="father_name")
        with col_name2:
            last_name = st.text_input("Soyad", key="last_name")
            position = st.text_input("Vəzifə", key="position")
        
        st.markdown('<div class="section-header"><h3>🏢 Təşkilat Məlumatları</h3></div>', unsafe_allow_html=True)
        department = st.selectbox("Şöbə", DEPARTMENTS, key="department")
        
        st.markdown('<div class="section-header"><h3>🧳 Ezamiyyət Məlumatları</h3></div>', unsafe_allow_html=True)
        trip_type = st.radio("Ezamiyyət növü", ["Ölkə daxili", "Ölkə xarici"], key="trip_type")
        
        destination = ""
        daily_allowance = 0
        
        if trip_type == "Ölkə daxili":
            col_route1, col_route2 = st.columns(2)
            with col_route1:
                from_city = st.selectbox("Haradan", CITIES, index=CITIES.index("Bakı"), key="from_city")
            with col_route2:
                available_cities = [city for city in CITIES if city != from_city]
                to_city = st.selectbox("Haraya", available_cities, key="to_city")
            
            destination = f"{from_city} → {to_city}"
            daily_allowance = calculate_domestic_amount(from_city, to_city)
        else:
            country = st.selectbox("Ölkə seçimi", list(COUNTRIES.keys()), key="country")
            destination = country
            daily_allowance = COUNTRIES[country]
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("Başlanğıc tarixi", key="start_date")
        with col_date2:
            end_date = st.date_input("Bitmə tarixi", key="end_date")
        
        purpose = st.text_area("Ezamiyyətin məqsədi", key="purpose")
        
    with col2:
        st.markdown('<div class="section-header"><h3>💰 Hesablama</h3></div>', unsafe_allow_html=True)
        
        if start_date and end_date and end_date >= start_date:
            trip_days = calculate_days(start_date, end_date)
            total_amount = daily_allowance * trip_days
            
            st.metric("Günlük məbləğ", f"{daily_allowance} AZN")
            st.metric("Ezamiyyət günləri", f"{trip_days} gün")
            st.metric("Ümumi məbləğ", f"{total_amount} AZN")
            
            if trip_type == "Ölkə xarici":
                usd_amount = total_amount / 1.7
                st.metric("USD ilə", f"${usd_amount:.2f}")
        
        if st.button("💾 Yadda Saxla", type="primary", use_container_width=True):
            if not all([first_name, last_name, father_name]):
                st.error("⚠️ Zəhmət olmasa, bütün məcburi sahələri doldurun!")
            elif end_date < start_date:
                st.error("⚠️ Bitmə tarixi başlanğıc tarixindən əvvəl ola bilməz!")
            else:
                trip_data = {
                    "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Ad": first_name,
                    "Soyad": last_name,
                    "Ata adı": father_name,
                    "Vəzifə": position or "Müəyyən edilməyib",
                    "Şöbə": department,
                    "Ezamiyyət növü": trip_type,
                    "Marşrut": destination,
                    "Başlanğıc tarixi": start_date.strftime("%Y-%m-%d"),
                    "Bitmə tarixi": end_date.strftime("%Y-%m-%d"),
                    "Günlər": trip_days,
                    "Günlük məbləğ": daily_allowance,
                    "Ümumi məbləğ": total_amount,
                    "Məqsəd": purpose or "Müəyyən edilməyib"
                }
                
                df_saved = save_trip_data(trip_data)
                st.success(f"✅ {first_name} {last_name} üçün ezamiyyət məlumatları yadda saxlanıldı!")
                st.balloons()

with tab2:
    st.markdown('<div class="section-header"><h3>📊 Ezamiyyət Statistikaları</h3></div>', unsafe_allow_html=True)
    
    df = load_trip_data()
    
    if not df.empty:
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        
        with col_stats1:
            st.metric("Ümumi ezamiyyət", len(df))
        with col_stats2:
            domestic_trips = len(df[df['Ezamiyyət növü'] == 'Ölkə daxili'])
            st.metric("Daxili ezamiyyət", domestic_trips)
        with col_stats3:
            international_trips = len(df[df['Ezamiyyət növü'] == 'Ölkə xarici'])
            st.metric("Xarici ezamiyyət", international_trips)
        with col_stats4:
            total_amount = df.get('Ümumi məbləğ', pd.Series([0]*len(df))).sum()
            st.metric("Ümumi xərc", f"{total_amount:,.0f} AZN")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            trip_counts = df['Ezamiyyət növü'].value_counts()
            fig_pie = px.pie(values=trip_counts.values, names=trip_counts.index, 
                           title="Ezamiyyət Növləri")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_chart2:
            df['Ay'] = pd.to_datetime(df['Tarix']).dt.to_period('M')
            monthly_trips = df.groupby('Ay').size()
            fig_line = px.line(x=monthly_trips.index.astype(str), y=monthly_trips.values, 
                             title="Aylıq Ezamiyyət Sayı")
            st.plotly_chart(fig_line, use_container_width=True)
        
        if 'Ümumi məbləğ' in df.columns:
            dept_stats = df.groupby('Şöbə').agg({
                'Ümumi məbləğ': 'sum',
                'Ad': 'count'
            }).rename(columns={'Ad': 'Ezamiyyət sayı'}).sort_values('Ümumi məbləğ', ascending=False)
        else:
            dept_stats = df.groupby('Şöbə').agg({
                'Ad': 'count'
            }).rename(columns={'Ad': 'Ezamiyyət sayı'})
            dept_stats['Ümumi məbləğ'] = 0
        
        st.subheader("Şöbələr üzrə statistika")
        st.dataframe(dept_stats, use_container_width=True)
        
    else:
        st.info("📋 Hələ ki məlumat mövcud deyil.")

with tab3:
    st.markdown('<div class="section-header"><h3>🔒 Admin Panel</h3></div>', unsafe_allow_html=True)
    
    col_admin1, col_admin2 = st.columns(2)
    
    with col_admin1:
        admin_username = st.text_input("İstifadəçi adı", key="admin_user")
    with col_admin2:
        admin_password = st.text_input("Şifrə", type="password", key="admin_pass")
    
    if st.button("🔓 Giriş", type="primary"):
        if admin_username == "admin" and admin_password == "admin123":
            st.success("✅ Uğurlu giriş!")
            
            df_admin = load_trip_data()
            
            if not df_admin.empty:
                st.subheader("📋 Bütün Ezamiyyət Məlumatları")
                st.dataframe(df_admin, use_container_width=True)
                
                col_export1, col_export2 = st.columns(2)
                
                with col_export1:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_admin.to_excel(writer, index=False, sheet_name='Ezamiyyət Məlumatları')
                        
                        summary_data = {
                            'Statistika': ['Ümumi ezamiyyət sayı', 'Daxili ezamiyyət', 'Xarici ezamiyyət', 'Ümumi xərc (AZN)'],
                            'Dəyər': [
                                len(df_admin),
                                len(df_admin[df_admin['Ezamiyyət növü'] == 'Ölkə daxili']),
                                len(df_admin[df_admin['Ezamiyyət növü'] == 'Ölkə xarici']),
                                df_admin.get('Ümumi məbləğ', pd.Series([0]*len(df_admin))).sum()
                            ]
                        }
                        pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Statistika')
                    
                    processed_data = output.getvalue()
                    
                    st.download_button(
                        label="📊 Excel Yüklə",
                        data=processed_data,
                        file_name=f"ezamiyyet_melumatlari_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with col_export2:
                    csv_data = df_admin.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📄 CSV Yüklə",
                        data=csv_data,
                        file_name=f"ezamiyyet_melumatlari_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                if st.checkbox("🗑️ Qeyd silmə rejimini aktiv et"):
                    selected_indices = st.multiselect(
                        "Silinəcək qeydləri seçin:",
                        options=df_admin.index,
                        format_func=lambda x: f"{df_admin.loc[x, 'Ad']} {df_admin.loc[x, 'Soyad']} - {df_admin.loc[x, 'Marşrut']}"
                    )
                    
                    if selected_indices and st.button("Seçilmiş qeydləri sil", type="secondary"):
                        df_admin_filtered = df_admin.drop(selected_indices)
                        df_admin_filtered.to_csv("ezamiyyet_melumatlari.csv", index=False)
                        st.success(f"✅ {len(selected_indices)} qeyd silindi!")
                        st.experimental_rerun()
                        
            else:
                st.warning("📋 Hələ ki məlumat mövcud deyil.")
                
        else:
            if admin_username or admin_password:
                st.error("❌ İstifadəçi adı və ya şifrə yanlışdır!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "© 2024 Azərbaycan Respublikası Dövlət Statistika Komitəsi | Ezamiyyət Hesablayıcı v2.0"
    "</div>", 
    unsafe_allow_html=True
)
