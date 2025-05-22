import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO
import requests
import os
from typing import Dict, List, Optional

# Konfiqurasiya
st.set_page_config(
    page_title="Ezamiyyət hesablayıcı", 
    page_icon="✈️",
    layout="wide"
)

# Sabitlər
CSV_FILE = "ezamiyyet_melumatlari.csv"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Şöbələr siyahısı (qısaldılmış versiya daha yaxşı UX üçün)
SOBELER: List[str] = [
    "Statistika işlərinin əlaqələndirilməsi və strateji planlaşdırma",
    "Keyfiyyətin idarə edilməsi və metaməlumatlar",
    "Milli hesablar və makroiqtisadi göstəricilər statistikası",
    "Kənd təsərrüfatı statistikası",
    "Sənaye və tikinti statistikası",
    "Energetika və ətraf mühit statistikası",
    "Ticarət statistikası",
    "Sosial statistika",
    "Xidmət statistikası",
    "Əmək statistikası",
    "Qiymət statistikası",
    "Əhali statistikası",
    "Həyat keyfiyyətinin statistikası",
    "Dayanıqlı inkişaf statistikası",
    "İnformasiya texnologiyaları",
    "İnformasiya və ictimaiyyətlə əlaqələr",
    "Beynəlxalq əlaqələr",
    "İnsan resursları və hüquq",
    "Maliyyə və təsərrüfat",
    "Ümumi şöbə",
    "Rejim və məxfi kargüzarlıq",
    "Elmi-Tədqiqat və Statistik İnnovasiyalar Mərkəzi",
    "Yerli statistika orqanları"
]

VEZIFELER: List[str] = [
    "Kiçik mütəxəssis",
    "Mütəxəssis", 
    "Baş mütəxəssis",
    "Şöbə müdiri",
    "Mühasib",
    "Analitik"
]

# Məbləğ xəritələri
DOMESTIC_RATES: Dict[str, int] = {
    "Bakı - Gəncə": 100,
    "Bakı - Şəki": 90,
    "Bakı - Lənkəran": 80,
    "Bakı - Sumqayıt": 50,
}

INTERNATIONAL_RATES: Dict[str, int] = {
    "Türkiyə": 300,
    "Gürcüstan": 250,
    "Almaniya": 600,
    "BƏƏ": 500,
    "Rusiya": 400,
}

# Utility funksiyaları
def validate_dates(start_date: date, end_date: date) -> bool:
    """Tarixlərin düzgünlüyünü yoxlayır"""
    return end_date >= start_date

def validate_required_fields(**fields) -> tuple[bool, str]:
    """Zəruri sahələrin doldurulmasını yoxlayır"""
    for field_name, field_value in fields.items():
        if not field_value or (isinstance(field_value, str) and not field_value.strip()):
            return False, f"{field_name} sahəsi doldurulmalıdır"
    return True, ""

def calculate_amount(destination: str, is_domestic: bool) -> int:
    """Ezamiyyət məbləğini hesablayır"""
    rates = DOMESTIC_RATES if is_domestic else INTERNATIONAL_RATES
    return rates.get(destination, 0)

def send_telegram_notification(message: str) -> bool:
    """Telegram bildirişi göndərir"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Telegram bildirişi göndərilərkən xəta: {e}")
        return False

def save_to_csv(data: Dict) -> bool:
    """Məlumatı CSV faylına saxlayır"""
    try:
        df_new = pd.DataFrame([data])
        
        if os.path.exists(CSV_FILE):
            df_existing = pd.read_csv(CSV_FILE)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Məlumat saxlanılarkən xəta: {e}")
        return False

def create_excel_file(data: Dict) -> BytesIO:
    """Excel faylı yaradır"""
    df = pd.DataFrame([data])
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ezamiyyət')
        
        # Sütunların genişliyini avtomatik tənzimləyir
        worksheet = writer.sheets['Ezamiyyət']
        for idx, col in enumerate(df.columns):
            max_len = max(len(str(col)), df[col].astype(str).str.len().max())
            worksheet.set_column(idx, idx, min(max_len + 2, 50))
    
    output.seek(0)
    return output

# Ana interfeys
def main():
    st.title("✈️ Ezamiyyət Məlumat Forması")
    
    # Session state-də məlumatları saxlamaq
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Formu bölmələrə ayırmaq
    with st.container():
        st.subheader("👤 Şəxsi məlumatlar")
        col1, col2 = st.columns(2)
        
        with col1:
            ad = st.text_input("Ad", value=st.session_state.form_data.get('ad', ''))
            soyad = st.text_input("Soyad", value=st.session_state.form_data.get('soyad', ''))
        
        with col2:
            ata_adi = st.text_input("Ata adı", value=st.session_state.form_data.get('ata_adi', ''))
            email = st.text_input("Email ünvanı", value=st.session_state.form_data.get('email', ''))
    
    with st.container():
        st.subheader("🏢 Vəzifə məlumatları")
        col1, col2 = st.columns(2)
        
        with col1:
            sobe = st.selectbox("Şöbə", SOBELER)
        with col2:
            vezife = st.selectbox("Vəzifə", VEZIFELER)
    
    with st.container():
        st.subheader("🧳 Ezamiyyət məlumatları")
        ezam_tip = st.radio("Ezamiyyət növü", ["Ölkə daxili", "Ölkə xarici"])
        
        # Destination seçimi
        is_domestic = ezam_tip == "Ölkə daxili"
        destinations = list(DOMESTIC_RATES.keys()) if is_domestic else list(INTERNATIONAL_RATES.keys())
        destination = st.selectbox("Hara ezam olunursunuz?", destinations)
        
        # Məbləği göstər
        amount = calculate_amount(destination, is_domestic)
        st.info(f"💰 Gündəlik məbləğ: **{amount} AZN**")
    
    with st.container():
        st.subheader("📅 Ezamiyyət dövrü")
        col1, col2 = st.columns(2)
        
        with col1:
            baslama_tarixi = st.date_input("Başlanğıc tarixi", value=date.today())
        with col2:
            bitme_tarixi = st.date_input("Bitmə tarixi", value=date.today())
        
        # Gün sayını hesabla
        if bitme_tarixi >= baslama_tarixi:
            gun_sayi = (bitme_tarixi - baslama_tarixi).days + 1
            umumi_mebleg = amount * gun_sayi
            st.success(f"📊 Ezamiyyət müddəti: **{gun_sayi} gün** | Ümumi məbləğ: **{umumi_mebleg} AZN**")
        else:
            st.error("Bitmə tarixi başlanğıc tarixindən kiçik ola bilməz!")
    
    # Əməliyyat düymələri
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Məlumatı saxla", type="primary", use_container_width=True):
            # Validasiya
            is_valid, error_msg = validate_required_fields(
                ad=ad, soyad=soyad, ata_adi=ata_adi, email=email
            )
            
            if not is_valid:
                st.error(error_msg)
            elif not validate_dates(baslama_tarixi, bitme_tarixi):
                st.error("Tarixlər düzgün deyil!")
            else:
                # Məlumatları hazırla
                gun_sayi = (bitme_tarixi - baslama_tarixi).days + 1
                umumi_mebleg = amount * gun_sayi
                
                data = {
                    "Tarix": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Ad": ad,
                    "Soyad": soyad,
                    "Ata adı": ata_adi,
                    "Email": email,
                    "Şöbə": sobe,
                    "Vəzifə": vezife,
                    "Ezamiyyət növü": ezam_tip,
                    "Yön": destination,
                    "Başlanğıc tarixi": baslama_tarixi.strftime("%Y-%m-%d"),
                    "Bitmə tarixi": bitme_tarixi.strftime("%Y-%m-%d"),
                    "Gün sayı": gun_sayi,
                    "Gündəlik məbləğ (AZN)": amount,
                    "Ümumi məbləğ (AZN)": umumi_mebleg
                }
                
                # Session state-ə saxla
                st.session_state.form_data = data
                
                # CSV-ə saxla
                if save_to_csv(data):
                    st.success("✅ Məlumat uğurla saxlanıldı!")
                    
                    # Telegram bildirişi
                    telegram_msg = (
                        f"✈️ Yeni ezamiyyət məlumatı:\n"
                        f"👤 {ad} {soyad} {ata_adi}\n"
                        f"📧 {email}\n"
                        f"🏢 {sobe}\n"
                        f"💼 {vezife}\n"
                        f"🧳 {ezam_tip}\n"
                        f"📍 {destination}\n"
                        f"📅 {baslama_tarixi} - {bitme_tarixi} ({gun_sayi} gün)\n"
                        f"💰 {umumi_mebleg} AZN"
                    )
                    
                    if send_telegram_notification(telegram_msg):
                        st.info("📱 Telegram bildirişi göndərildi")
    
    with col2:
        if st.button("📥 Excel yüklə", use_container_width=True):
            if not st.session_state.form_data:
                st.error("Əvvəlcə məlumatı saxlayın!")
            else:
                excel_file = create_excel_file(st.session_state.form_data)
                
                st.download_button(
                    label="📁 Excel faylını yüklə",
                    data=excel_file.getvalue(),
                    file_name=f"ezamiyyet_{ad}_{soyad}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    # Statistika bölməsi
    if os.path.exists(CSV_FILE):
        st.divider()
        st.subheader("📊 Statistika")
        
        try:
            df = pd.read_csv(CSV_FILE)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Ümumi ezamiyyət sayı", len(df))
            with col2:
                st.metric("Ümumi xərc", f"{df['Ümumi məbləğ (AZN)'].sum()} AZN")
            with col3:
                st.metric("Orta məbləğ", f"{df['Ümumi məbləğ (AZN)'].mean():.0f} AZN")
            
            # Son 5 ezamiyyət
            if st.checkbox("Son ezamiyyətləri göstər"):
                st.dataframe(df.tail().sort_values('Tarix', ascending=False), use_container_width=True)
                
        except Exception as e:
            st.error(f"Statistika yüklənərkən xəta: {e}")

if __name__ == "__main__":
    main()
