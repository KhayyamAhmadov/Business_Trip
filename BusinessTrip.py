import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Ezamiyyət hesablayıcı", page_icon="✈️")

# Sadə sayt şifrəsi
st.title("✈️ Ezamiyyət hesablayıcı - Giriş")
password = st.text_input("Sayta giriş üçün şifrəni daxil edin:", type="password")

# Daxil ediləcək şifrə
correct_password = "admin"

if password != correct_password:
    st.warning("Zəhmət olmasa düzgün şifrəni daxil edin.")
    st.stop()  # Saytın digər hissələri açılmasın

# --- Əsas app hissəsi ---

st.title("✈️ Ezamiyyət Məlumat Forması")

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

seherler = [
    "Abşeron", "Ağcabədi", "Ağdam", "Ağdaş", "Ağdərə", "Ağstafa", "Ağsu",
    "Astara", "Bakı", "Babək (Naxçıvan MR)", "Balakən", "Bərdə", "Beyləqan",
    "Biləsuvar", "Cəbrayıl", "Cəlilabad", "Culfa (Naxçıvan MR)", "Daşkəsən",
    "Füzuli", "Gədəbəy", "Gəncə", "Goranboy", "Göyçay", "Göygöl", "Hacıqabul",
    "Xaçmaz", "Xankəndi", "Xızı", "Xocalı", "Xocavənd", "İmişli", "İsmayıllı",
    "Kəlbəcər", "Kəngərli (Naxçıvan MR)", "Kürdəmir", "Laçın", "Lənkəran",
    "Lerik", "Masallı", "Mingəçevir", "Naftalan", "Neftçala", "Naxçıvan",
    "Oğuz", "Ordubad (Naxçıvan MR)", "Qəbələ", "Qax", "Qazax", "Qobustan",
    "Quba", "Qubadlı", "Qusar", "Saatlı", "Sabirabad", "Sədərək (Naxçıvan MR)",
    "Salyan", "Samux", "Şabran", "Şahbuz (Naxçıvan MR)", "Şamaxı", "Şəki",
    "Şəmkir", "Şərur (Naxçıvan MR)", "Şirvan", "Şuşa", "Sumqayıt", "Tərtər",
    "Tovuz", "Ucar", "Yardımlı", "Yevlax", "Zaqatala", "Zəngilan", "Zərdab"
]

st.subheader("👤 Şəxsi məlumatlar")
ad = st.text_input("Ad")
soyad = st.text_input("Soyad")
ata_adi = st.text_input("Ata adı")

st.subheader("🏢 Şöbə seçimi")
sobe = st.selectbox("Hansə şöbədə işləyirsiniz?", sobeler)

st.subheader("🚩 Haradan/Hara ezam olunursunuz?")

hardan = st.selectbox("Haradan", seherler)
haraya = st.selectbox("Haraya", seherler)

# Ödəniş növü radio düymələri ilə
st.subheader("💳 Ödəniş növü seçimi")
odenis_novu = st.radio("Ödəniş seçin:", ["Ödənişsiz", "10% ödəniş edilərək", "Tam ödəniş"])

st.subheader("🧳 Ezamiyyət növü")
ezam_tip = st.radio("Ezamiyyət ölkə daxili, yoxsa ölkə xaricidir?", ["Ölkə daxili", "Ölkə xarici"])

amount_map_daxili = {
    # Sənin əvvəldə verdiyin nümunəyə görə, hardan-haraya fərqli qiymət lazım ola bilər, amma
    # sadə nümunə üçün elə "Haradan - Haraya" kimi birləşdirib qiymət verək:
    f"{hardan} - {haraya}": 100  # sadəcə nümunə, lazım gələrsə xəritə genişləndirmək olar
}

amount_map_xarici = {
    "Türkiyə": 300,
    "Gürcüstan": 250,
    "Almaniya": 600,
    "BƏƏ": 500,
    "Rusiya": 400,
}

if ezam_tip == "Ölkə daxili":
    # Daxili üçün seçilmiş hardan-haraya uyğun məbləğ
    # Əgər xəritə genişdirsə, xüsusi qiymətlər ola bilər
    # Burada sadə şəkildə hardan-haraya uyğun qiymət yoxlamaq üçün nümunə
    # Əslində bu hissəni genişləndirə bilərsən
    if hardan == haraya:
        mebleg = 0
    else:
        mebleg = 100  # hardan-haraya fərqli qiymət təyin etmək üçün burada dəyişmək olar
else:
    mebleg = amount_map_xarici.get(st.selectbox("Hansı ölkəyə ezam olunursunuz?", list(amount_map_xarici.keys())), 0)

# Ödəniş növünə görə məbləğ tənzimlənməsi
if odenis_novu == "Ödənişsiz":
    mebleg_final = 0
elif odenis_novu == "10% ödəniş edilərək":
    mebleg_final = mebleg * 0.1
else:  # Tam ödəniş
    mebleg_final = mebleg

st.subheader("📅 Ezamiyyət dövrü")
baslama_tarixi = st.date_input("Başlanğıc tarixi")
bitme_tarixi = st.date_input("Bitmə tarixi")

if st.button("💰 Ödəniləcək məbləği göstər"):
    if not (ad and soyad and ata_adi):
        st.error("Zəhmət olmasa, ad, soyad və ata adını daxil edin!")
    elif bitme_tarixi < baslama_tarixi:
        st.error("Bitmə tarixi başlanğıc tarixindən kiçik ola bilməz!")
    elif hardan == haraya:
        st.error("Haradan və haraya eyni şəhəri seçmək olmaz!")
    else:
        indiki_vaxt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"👤 {ad} {soyad} {ata_adi} üçün ezamiyyət məbləği: **{mebleg_final:.2f} AZN**")
        st.info(f"🕒 Məlumat daxil edilmə vaxtı: {indiki_vaxt}")

        new_data = {
            "Tarix": [indiki_vaxt],
            "Ad": [ad],
            "Soyad": [soyad],
            "Ata adı": [ata_adi],
            "Şöbə": [sobe],
            "Haradan": [hardan],
            "Haraya": [haraya],
            "Ödəniş növü": [odenis_novu],
            "Ezamiyyət növü": [ezam_tip],
            "Başlanğıc tarixi": [baslama_tarixi.strftime("%Y-%m-%d")],
            "Bitmə tarixi": [bitme_tarixi.strftime("%Y-%m-%d")],
            "Məbləğ": [mebleg_final]
        }
        df_new = pd.DataFrame(new_data)

        try:
            df_existing = pd.read_csv("ezamiyyet_melumatlari.csv")
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new

        df_combined.to_csv("ezamiyyet_melumatlari.csv", index=False)
        st.info("📁 Məlumat uğurla yadda saxlanıldı.")


# admin girisi hissesi 
st.subheader("🔒 Admin bölməsi")

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
        st.error("İstifadəçi adı və ya şifrə yalnışdır.")
