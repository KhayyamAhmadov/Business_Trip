import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import os

# Streamlit səhifə konfiqurasiyası
st.set_page_config(page_title="Ezamiyyət hesablayıcı", page_icon="✈️")

# Başlıq
st.title("✈️ Ezamiyyət Məlumat Forması")

# Şöbə siyahısı
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

# Vəzifə siyahısı
vezifeler = [
    "Kiçik mütəxəssis",
    "Baş mütəxəssis",
    "Şöbə müdiri",
    "Mühasib",
    "Analitik",
    "Mütəxəssis",
]

# Telegram Bot Token və Chat ID (öz məlumatlarını əlavə et!)
TELEGRAM_BOT_TOKEN = "BOT_TOKENUNUZU_BURAYA_YAZIN"
TELEGRAM_CHAT_ID = "CHAT_ID_NIZI_BURAYA_YAZIN"

# 🧾 Form məlumatları
st.subheader("👤 Şəxsi Məlumatlar")
ad = st.text_input("Ad")
soyad = st.text_input("Soyad")
ata_adi = st.text_input("Ata adı")
email = st.text_input("Email ünvanı")

st.subheader("🏢 İş məlumatları")
sobe = st.selectbox("Şöbə seçin", sobeler)
vezife = st.selectbox("Vəzifə seçin", vezifeler)

st.subheader("🌍 Ezamiyyət məlumatları")
ezam_tip = st.radio("Ezamiyyət növü:", ["Ölkə daxili", "Ölkə xarici"])

if ezam_tip == "Ölkə daxili":
    destination = st.selectbox("Şəhər seçin", ["Bakı - Gəncə", "Bakı - Şəki", "Bakı - Lənkəran", "Bakı - Sumqayıt"])
    mebleg_map = {
        "Bakı - Gəncə": 100,
        "Bakı - Şəki": 90,
        "Bakı - Lənkəran": 80,
        "Bakı - Sumqayıt": 50,
    }
else:
    destination = st.selectbox("Ölkə seçin", ["Türkiyə", "Gürcüstan", "Almaniya", "BƏƏ", "Rusiya"])
    mebleg_map = {
        "Türkiyə": 300,
        "Gürcüstan": 250,
        "Almaniya": 600,
        "BƏƏ": 500,
        "Rusiya": 400,
    }

mebleg = mebleg_map.get(destination, 0)

st.subheader("📅 Tarix Seçimi")
baslama_tarixi = st.date_input("Başlama tarixi")
bitme_tarixi = st.date_input("Bitmə tarixi")

# Əsas düymə
if st.button("💾 Yadda saxla və Telegram-a göndər"):
    if not all([ad, soyad, ata_adi, email]):
        st.error("Zəhmət olmasa, bütün şəxsi məlumatları daxil edin!")
    elif bitme_tarixi < baslama_tarixi:
        st.error("Bitmə tarixi başlanğıc tarixindən erkən ola bilməz!")
    else:
        # Məlumatların hazırlanması
        tarix = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yeni_melumat = {
            "Tarix": tarix,
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
            "Məbləğ (AZN)": mebleg
        }

        # CSV faylına yazmaq
        fayl_adi = "ezamiyyet_melumatlari.csv"
        fayl_movcuddur = os.path.exists(fayl_adi)

        df_yeni = pd.DataFrame([yeni_melumat])

        if fayl_movcuddur:
            df_kohne = pd.read_csv(fayl_adi)
            df_birlesmis = pd.concat([df_kohne, df_yeni], ignore_index=True)
        else:
            df_birlesmis = df_yeni

        df_birlesmis.to_csv(fayl_adi, index=False)

        # Telegram bildirişi
        mesaj = (
            f"📤 Yeni ezamiyyət məlumatı daxil edildi:\n\n"
            f"👤 {ad} {soyad} {ata_adi}\n"
            f"🏢 Şöbə: {sobe}\n"
            f"📌 Ezamiyyet: {destination} ({ezam_tip})\n"
            f"📅 {baslama_tarixi.strftime('%d.%m.%Y')} - {bitme_tarixi.strftime('%d.%m.%Y')}\n"
            f"💰 Məbləğ: {mebleg} AZN\n"
            f"📥 Email: {email}\n"
            f"🕒 Yaradılma: {tarix}"
        )

        def telegram_bildiris_gonder(metin):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": metin
            }
            response = requests.post(url, data=data)
            return response

        cavab = telegram_bildiris_gonder(mesaj)

        if cavab.status_code == 200:
            st.success("Məlumat uğurla yadda saxlanıldı və Telegram-a göndərildi ✅")
        else:
            st.warning("Məlumat yadda saxlanıldı, lakin Telegram bildirişi göndərilə bilmədi ❗")

        # CSV faylını yükləmək üçün düymə
        st.download_button(
            label="📂 CSV faylını yüklə",
            data=df_birlesmis.to_csv(index=False).encode("utf-8"),
            file_name="ezamiyyet_melumatlari.csv",
            mime="text/csv"
        )


# admin girisi hissesi 
st.subheader("🔒 Admin bölməsi: Daxil edilmiş məlumatların siyahısı")

admin_username = st.text_input("Admin istifadəçi adı daxil edin")
admin_password = st.text_input("Admin şifrəni daxil edin", type="password")

if admin_username == "admin" and admin_password == "admin":
    try:
        df_admin = pd.read_csv("ezamiyyet_melumatlari.csv")
        st.dataframe(df_admin)
    
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_admin.to_excel(writer, index=False, sheet_name='Ezamiyyet')
        processed_data = output.getvalue()
    
        st.download_button(
            label="Excel faylını yüklə",
            data=processed_data,
            file_name="ezamiyyet_melumatlari.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except FileNotFoundError:
        st.warning("Hələ heç bir məlumat daxil edilməyib.")

else:
    if admin_username or admin_password:
        st.error("İstifadəçi adı və ya şifrə yalnışdır!")
