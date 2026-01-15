import streamlit as st
from fpdf import FPDF
import base64
import os

# 1. OXFORD CV TASARIM SINIFI
class OxfordCV(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Windows sistemlerde Türkçe karakter desteği için Arial fontu yolu
        font_path = r"C:\Windows\Fonts\arial.ttf"
        font_path_bold = r"C:\Windows\Fonts\arialbd.ttf"
        font_path_italic = r"C:\Windows\Fonts\ariali.ttf"
        
        if os.path.exists(font_path):
            self.add_font("TRFont", "", font_path)
            self.add_font("TRFont", "B", font_path_bold)
            self.add_font("TRFont", "I", font_path_italic)
            self.main_font = "TRFont"
        else:
            self.main_font = "Helvetica" # Font bulunamazsa standart font

    def header(self):
        # Sadece 1. sayfada Ad-Soyad ve iletişim bilgilerini göster
        if self.page_no() == 1 and hasattr(self, 'user_data'):
            self.set_font(self.main_font, 'B', 22)
            self.cell(0, 12, self.user_data['ad'].upper(), ln=True, align='C')
            self.set_font(self.main_font, '', 10)
            contact = f"{self.user_data['adres']} | {self.user_data['tel']} | {self.user_data['email']}"
            self.cell(0, 5, contact, ln=True, align='C')
            self.set_line_width(0.5)
            self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
            self.ln(8)
        else:
            # 2. sayfada üstten küçük bir boşluk bırak
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.main_font, 'I', 8)
        page_text = "Sayfa" if self.user_data['lang'] == "Türkçe" else "Page"
        self.cell(0, 10, f'{page_text} {self.page_no()}', align='C')

    def bolum_basligi(self, baslik):
        self.ln(2)
        self.set_font(self.main_font, 'B', 12)
        self.cell(0, 8, baslik.upper(), ln=True)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def icerik_ekle(self, kurum, tarih, baslik, detay):
        # Sol üst: Kurum/Başlık (Kalın), Sağ üst: Tarih (İtalik)
        self.set_font(self.main_font, 'B', 11)
        self.cell(130, 6, kurum)
        self.set_font(self.main_font, 'I', 11)
        self.cell(60, 6, tarih, ln=True, align='R')
        # Alt başlık (Pozisyon/Bölüm - İtalik)
        if baslik:
            self.set_font(self.main_font, 'I', 10)
            self.cell(0, 5, baslik, ln=True)
        # Açıklama metni
        self.set_font(self.main_font, '', 10)
        if detay:
            self.multi_cell(0, 5, f"- {detay}")
        self.ln(2)

    def sade_metin_ekle(self, metin):
        self.set_font(self.main_font, '', 10)
        self.multi_cell(0, 5, metin)
        self.ln(2)

# 2. DİL PAKETLERİ VE BAŞLIKLAR
dil_paketleri = {
    "Türkçe": {
        "hakkimda": "Hakkımda", "deneyim": "İş Deneyimi", "egitim": "Eğitim",
        "diller": "Dil Becerileri", "yetenekler": "Yetenekler", "projeler": "Projeler",
        "sertifikalar": "Sertifikalar", "basarilar": "Başarılar", "gonulluluk": "Gönüllülük",
        "referanslar": "Referanslar", "buton": "Önizlemeyi Güncelle / Oluştur", "indir": "İndir"
    },
    "English": {
        "hakkimda": "Summary", "deneyim": "Work Experience", "egitim": "Education",
        "diller": "Languages", "yetenekler": "Skills", "projeler": "Projects",
        "sertifikalar": "Certifications", "basarilar": "Honors & Awards", "gonulluluk": "Volunteering",
        "referanslar": "References", "buton": "Update Preview / Create CV", "indir": "Download"
    }
}

# 3. STREAMLIT ARAYÜZÜ
st.set_page_config(page_title="Oxford Professional CV", layout="wide")
secilen_dil = st.sidebar.selectbox("Dil / Language", ["Türkçe", "English"])
p = dil_paketleri[secilen_dil]

col_form, col_preview = st.columns([1, 1])

with col_form:
    st.title(f"🎓 Oxford {secilen_dil} CV Builder")
    with st.form("cv_pro_form"):
        ad = st.text_input("Ad Soyad / Full Name")
        email = st.text_input("E-posta / Email")
        tel = st.text_input("Telefon / Phone")
        adres = st.text_input("Adres / Address")
        
        # Giriş Alanları (Sıralı)
        hakkimda = st.text_area(p["hakkimda"])
        deneyim = st.text_area(p["deneyim"] + " (Kurum | Tarih | Pozisyon | Detay)")
        egitim = st.text_area(p["egitim"] + " (Kurum | Tarih | Bölüm | Detay)")
        diller = st.text_input(p["diller"])
        yetenekler = st.text_area(p["yetenekler"])
        projeler = st.text_area(p["projeler"] + " (Proje Adı | Tarih | Rol | Detay)")
        sertifikalar = st.text_area(p["sertifikalar"] + " (Sertifika Adı | Tarih | Kurum | Detay)")
        basarilar = st.text_area(p["basarilar"] + " (Başarı Adı | Tarih | Kurum | Detay)")
        gonulluluk = st.text_area(p["gonulluluk"])
        referanslar = st.text_area(p["referanslar"] + " (Ad | Ünvan | İletişim | İlişki)")
        
        submitted = st.form_submit_button(p["buton"])

# 4. PDF ÜRETİM MANTIĞI
if ad:
    pdf = OxfordCV()
    pdf.user_data = {"ad": ad, "email": email, "tel": tel, "adres": adres, "lang": secilen_dil}
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def isle_liste(input_text, baslik_key):
        if input_text:
            pdf.bolum_basligi(p[baslik_key])
            for satir in input_text.split('\n'):
                if '|' in satir:
                    parcalar = satir.split('|')
                    while len(parcalar) < 4: parcalar.append("")
                    pdf.icerik_ekle(parcalar[0].strip(), parcalar[1].strip(), parcalar[2].strip(), parcalar[3].strip())

    def isle_sade(input_text, baslik_key):
        if input_text:
            pdf.bolum_basligi(p[baslik_key])
            pdf.sade_metin_ekle(input_text)

    # KESİN SIRALAMA (1-10)
    if hakkimda: isle_sade(hakkimda, "hakkimda")           # 1
    isle_liste(deneyim, "deneyim")                         # 2
    isle_liste(egitim, "egitim")                           # 3
    if diller: isle_sade(diller, "diller")                 # 4
    if yetenekler: isle_sade(yetenekler, "yetenekler")     # 5
    isle_liste(projeler, "projeler")                       # 6
    isle_liste(sertifikalar, "sertifikalar")               # 7 (Liste formatı)
    isle_liste(basarilar, "basarilar")                     # 8 (Liste formatı)
    if gonulluluk: isle_sade(gonulluluk, "gonulluluk")     # 9
    isle_liste(referanslar, "referanslar")                 # 10

    pdf_bytes = bytes(pdf.output())
    
    with col_preview:
        st.subheader("👀 Preview")
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        st.download_button(f"📥 {p['indir']} PDF", data=pdf_bytes, file_name=f"Oxford_CV_{secilen_dil}.pdf")