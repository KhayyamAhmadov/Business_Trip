import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import requests

st.set_page_config(page_title="Ezamiyyət hesablayıcı", page_icon="✈️")

st.title("✈️ Ezamiyyət Məlumat Forması")

# Şöbələr tam siyahısı
sobeler = [
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

vezifeler = [
    "Kiçik mütəxəssis",
    "Baş mütəxəssis",
    "Şöbə müdiri",
    "Mühasib",
    "Analitik",
    "Mütəxəssis",
]

# İstifadəçi məlumatları
st.subheader("👤 Şəxsi məlumatlar")
ad = st.text_input("Ad")
soyad = st.text_input("Soyad")
ata_adi = st.text_input("Ata adı")
email = st.text_input("Email ünvanı (bildiriş üçün)")

# Şöbə seçimi
st.subheader("🏢 Şöbə seçimi")
sobe = st.selectbox("Hansə şöbədə işləyirsiniz?", sobeler)

# Vəzifə seçimi
vezife = st.selectbox("Vəzifəniz nədir?", vezifeler)

# Ezamiyyət tipi
st.subheader("🧳 Ezamiyyət növü")
ezam_tip = st.radio("Ezamiyyət ölkə daxili, yoxsa ölkə xaricidir?", ["Ölkə daxili", "Ölkə xarici"])

# Hara gedir?
destination = ""
if ezam_tip == "Ölkə daxili":
    destination = st.selectbox("Hara ezam olunursunuz?", [
        "Bakı - Gəncə", "Bakı - Şəki", "Bakı - Lənkəran", "Bakı - Sumqayıt"
    ])
    amount_map = {
        "Bakı - Gəncə": 100,
        "Bakı - Şəki": 90,
        "Bakı - Lənkəran": 80,
        "Bakı - Sumqayıt": 50,
    }
else:
    destination = st.selectbox("Hansı ölkəyə ezam olunursunuz?", [
        "Türkiyə", "Gürcüstan", "Almaniya", "BƏƏ", "Rusiya"
    ])
    amount_map = {
        "Türkiyə": 300,
        "Gürcüstan": 250,
        "Almaniya": 600,
        "BƏƏ": 500,
        "Rusiya": 400,
    }

# Ezamiyyətin başlanğıc və son tarixləri
st.subheader("📅 Ezamiyyət dövrü")
baslama_tarixi = st.date_input("Başlanğıc tarixi")
bitme_tarixi = st.date_input("Bitmə tarixi")

mebleg = amount_map.get(destination, 0)

# Telegram Bot Parametrləri
TELEGRAM_BOT_TOKEN = "BOT_TOKENUNUZU_BURAYA_YAZIN"
TELEGRAM_CHAT_ID = "CHAT_ID_NIZI_BURAYA_YAZIN"

def telegram_bildiris_gonder(metin):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": metin}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Telegram bildirişi göndərilərkən xəta baş verdi: {e}")

if st.button("💰 Ödəniləcək məbləği göstər və yadda saxla"):
    if not (ad and soyad and ata_adi and email):
        st.error("Zəhmət olmasa, ad, soyad, ata adı və email daxil edin!")
    elif bitme_tarixi < baslama_tarixi:
        st.error("Bitmə tarixi başlanğıc tarixindən kiçik ola bilməz!")
    else:
        indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"👤 {ad} {soyad} {ata_adi} üçün ezamiyyət məbləği: **{mebleg} AZN**")
        st.info(f"🕒 Məlumat daxil edilmə vaxtı: {indiki_vaxt}")

        # Məlumatı CSV-ə əlavə et
        new_data = {
            "Tarix": [indiki_vaxt],
            "Ad": [ad],
            "Soyad": [soyad],
            "Ata adı": [ata_adi],
            "Email": [email],
            "Şöbə": [sobe],
            "Vəzifə": [vezife],
            "Ezamiyyət növü": [ezam_tip],
            "Yön": [destination],
            "Başlanğıc tarixi": [baslama_tarixi.strftime("%Y-%m-%d")],
            "Bitmə tarixi": [bitme_tarixi.strftime("%Y-%m-%d")],
            "Məbləğ": [mebleg]
        }
        df_new = pd.DataFrame(new_data)

        try:
            df_existing = pd.read_csv("ezamiyyet_melumatlari.csv")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new

        df_combined.to_csv("ezamiyyet_melumatlari.csv", index=False)
        st.info("📁 Məlumat uğurla yadda saxlanıldı!")

        # Telegrama bildiriş göndər
        bildiris_metin = (f"✈️ Yeni ezamiyyət məlumatı daxil edildi:\n"
                          f"👤 {ad} {soyad} {ata_adi}\n"
                          f"📧 Email: {email}\n"
                          f"🏢 Şöbə: {sobe}\n"
                          f"💼 Vəzifə: {vezife}\n"
                          f"🧳 Ezamiyyət növü: {ezam_tip}\n"
                          f"📍 Yön: {destination}\n"
                          f"📅 Dövr: {baslama_tarixi} - {bitme_tarixi}\n"
                          f"💰 Məbləğ: {mebleg} AZN")
        telegram_bildiris_gonder(bildiris_metin)

# Excel faylının yüklənməsi üçün ayrıca bölmə
st.subheader("📥 Excel faylını yüklə")

if st.button("Excel faylını hazırla və yüklə"):
    if not (ad and soyad and ata_adi):
        st.error("Excel faylı yaratmaq üçün əvvəlcə ad, soyad və ata adını daxil edin!")
    else:
        data = {
            "Ad": [ad],
            "Soyad": [soyad],
            "Ata adı": [ata_adi],
            "Email": [email],
            "Şöbə": [sobe],
            "Vəzifə": [vezife],
            "Ezamiyyət növü": [ezam_tip],
            "Yön": [destination],
            "Başlanğıc tarixi": [baslama_tarixi.strftime("%Y-%m-%d")],
            "Bitmə tarixi": [bitme_tarixi.strftime("%Y-%m-%d")],
            "Məbləğ (AZN)": [mebleg]
        }
        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Ezamiyyət')
            writer.save()
            processed_data = output.getvalue()

        st.download_button(
            label="Excel faylını yüklə",
            data=processed_data,
            file_name=f"ezamiyyet_{ad}_{soyad}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )



# admin girisi hissesi 
st.subheader("🔒 Admin bölməsi: Daxil edilmiş məlumatların siyahısı")

admin_username = st.text_input("Admin istifadəçi adı daxil edin")
admin_password = st.text_input("Admin şifrəni daxil edin", type="password")

# Sadə olaraq birləşdirilmiş yoxlama:
if admin_username == "admin" and admin_password == "admin":
    try:
        df_admin = pd.read_csv("ezamiyyet_melumatlari.csv")
        st.dataframe(df_admin)
    except FileNotFoundError:
        st.warning("Hələ heç bir məlumat daxil edilməyib.")
else:
    if admin_username or admin_password:  # Hər hansı biri daxil edilibsə
        st.error("İstifadəçi adı və ya şifrə yalnışdır!")
