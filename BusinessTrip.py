import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Ezamiyyət hesablayıcı", page_icon="✈️")

st.title("✈️ Ezamiyyət Məlumat Forması")

# İstifadəçi məlumatları
st.subheader("👤 Şəxsi məlumatlar")
ad = st.text_input("Ad")
soyad = st.text_input("Soyad")
ata_adi = st.text_input("Ata adı")
email = st.text_input("Email ünvanı")

# Şöbə seçimi
st.subheader("🏢 Şöbə seçimi")
sobe = st.selectbox("Hansə şöbədə işləyirsiniz?", [
    "Maliyyə", "İT", "HR", "Satış", "Marketinq"
])

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

def send_email_with_attachment(to_email, subject, body, attachment_data, filename):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = "sənin_email@gmail.com"
        msg["To"] = to_email
        msg.set_content(body)

        msg.add_attachment(attachment_data.read(), maintype='application',
                           subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           filename=filename)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("sənin_email@gmail.com", "TƏTBİQ_ŞİFRƏSİ")  # App password
            smtp.send_message(msg)

        return True
    except Exception as e:
        st.error(f"E-poçt göndərilərkən xəta baş verdi: {e}")
        return False

if st.button("💰 Ödəniləcək məbləği göstər, yadda saxla və göndər"):
    if not (ad and soyad and ata_adi and email):
        st.error("Zəhmət olmasa, bütün məlumatları doldurun, o cümlədən email!")
    elif bitme_tarixi < baslama_tarixi:
        st.error("Bitmə tarixi başlanğıc tarixindən kiçik ola bilməz!")
    else:
        indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"👤 {ad} {soyad} {ata_adi} üçün ezamiyyət məbləği: **{mebleg} AZN**")
        st.info(f"🕒 Məlumat daxil edilmə vaxtı: {indiki_vaxt}")

        # Məlumat çərçivəsi
        data = {
            "Tarix": [indiki_vaxt],
            "Ad": [ad],
            "Soyad": [soyad],
            "Ata adı": [ata_adi],
            "Email": [email],
            "Şöbə": [sobe],
            "Ezamiyyət növü": [ezam_tip],
            "Yön": [destination],
            "Başlanğıc tarixi": [baslama_tarixi.strftime("%Y-%m-%d")],
            "Bitmə tarixi": [bitme_tarixi.strftime("%Y-%m-%d")],
            "Məbləğ": [mebleg]
        }

        df = pd.DataFrame(data)

        # Excel faylını yadda saxla
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Ezamiyyət")
        output.seek(0)

        # Məlumatı CSV faylına əlavə et
        try:
            df_existing = pd.read_csv("ezamiyyet_melumatlari.csv")
            df_combined = pd.concat([df_existing, df], ignore_index=True)
        except FileNotFoundError:
            df_combined = df

        df_combined.to_csv("ezamiyyet_melumatlari.csv", index=False)
        st.success("📁 Məlumat yadda saxlanıldı.")

        # Email göndər
        subject = "Ezamiyyət məlumat faylınız"
        body = f"Hörmətli {ad} {soyad},\nEzamiyyət məlumatlarınızı əlavə olunmuş Excel faylında tapa bilərsiniz."
        success = send_email_with_attachment(email, subject, body, output, f"{ad}_{soyad}.xlsx")

        if success:
            st.success("📧 Email uğurla göndərildi!")

# Admin görünüşü
with st.expander("📊 Girişləri göstər (admin görünüşü)"):
    try:
        df = pd.read_csv("ezamiyyet_melumatlari.csv")
        st.dataframe(df)
    except FileNotFoundError:
        st.warning("Heç bir qeyd yoxdur.")
