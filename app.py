import streamlit as st
from fpdf import FPDF
import base64
import os

# ==============================
# 1. ATS UYUMLU PDF SINIFI
# ==============================
class OxfordCV(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_font = "Helvetica"

        font_path = r"C:\Windows\Fonts\arial.ttf"
        font_path_b = r"C:\Windows\Fonts\arialbd.ttf"

        if os.path.exists(font_path):
            self.add_font("ArialTR", "", font_path, uni=True)
            self.add_font("ArialTR", "B", font_path_b, uni=True)
            self.main_font = "ArialTR"

    def header(self):
        if self.page_no() == 1 and hasattr(self, "user_data"):
            self.set_font(self.main_font, "B", 18)
            self.cell(0, 10, self.user_data["ad"].upper(), ln=True, align="C")

            self.set_font(self.main_font, "", 10)
            contact = f"{self.user_data['adres']} | {self.user_data['tel']} | {self.user_data['email']}"
            self.cell(0, 6, contact, ln=True, align="C")
            self.ln(6)

    def bolum_basligi(self, baslik):
        self.ln(2)
        self.set_font(self.main_font, "B", 11)
        self.set_x(self.l_margin)
        self.cell(0, 6, baslik.upper(), ln=True)
        self.ln(1)

    def blok_ekle(self, baslik, tarih, alt_baslik, detay):
        # Başlık + Tarih
        self.set_x(self.l_margin)
        self.set_font(self.main_font, "B", 10)
        self.cell(120, 6, baslik, ln=0)

        self.set_font(self.main_font, "", 10)
        self.cell(0, 6, tarih, ln=1, align="R")

        # Alt başlık (Pozisyon / Kurum)
        if alt_baslik:
            self.set_x(self.l_margin)
            self.set_font(self.main_font, "B", 9.5)
            self.multi_cell(0, 5, alt_baslik)

        # Açıklama
        self.set_font(self.main_font, "", 9.5)
        if detay:
            for satir in detay.split("\n"):
                if satir.strip():
                    self.set_x(self.l_margin)
                    self.multi_cell(0, 5, "- " + satir.strip())

        self.ln(2)

# ==============================
# 2. DİL PAKETLERİ
# ==============================
dil_paketleri = {
    "Türkçe": {
        "hakkimda": "Hakkımda",
        "deneyim": "İş Deneyimi",
        "egitim": "Eğitim",
        "diller": "Diller",
        "yetenekler": "Yetenekler",
        "projeler": "Projeler",
        "sertifikalar": "Sertifikalar",
        "basarilar": "Ödüller",
        "gonulluluk": "Gönüllülük",
        "referanslar": "Referanslar",
        "buton": "Oluştur",
        "indir": "PDF İndir"
    },
    "English": {
        "hakkimda": "Summary",
        "deneyim": "Work Experience",
        "egitim": "Education",
        "diller": "Languages",
        "yetenekler": "Skills",
        "projeler": "Projects",
        "sertifikalar": "Certifications",
        "basarilar": "Honors & Awards",
        "gonulluluk": "Volunteering",
        "referanslar": "References",
        "buton": "Generate",
        "indir": "Download PDF"
    }
}

# ==============================
# 3. STREAMLIT UI
# ==============================
st.set_page_config(page_title="Oxford CV ATS", layout="wide")

secilen_dil = st.sidebar.radio("Language", ["Türkçe", "English"], horizontal=True)
p = dil_paketleri[secilen_dil]

bolumler = [
    "hakkimda", "deneyim", "egitim", "diller",
    "yetenekler", "projeler", "sertifikalar",
    "basarilar", "gonulluluk", "referanslar"
]

st.sidebar.subheader("🔢 Bölüm Sıralaması")
sirali_anahtarlar = []

for i in range(1, 11):
    secim = st.sidebar.selectbox(
        f"{i}. Bölüm",
        ["(Boş)"] + [p[b] for b in bolumler],
        key=f"secim_{i}"
    )
    if secim != "(Boş)":
        key = [k for k, v in p.items() if v == secim][0]
        if key not in sirali_anahtarlar:
            sirali_anahtarlar.append(key)

# ==============================
# 4. FORM
# ==============================
col_form, col_preview = st.columns([1, 1])

with col_form:
    st.title("📄 CV Bilgileri")

    with st.form("cv_form"):
        ad = st.text_input("Ad Soyad")
        email = st.text_input("E-posta")
        tel = st.text_input("Telefon")
        adres = st.text_input("Adres")

        inputs = {}
        st.markdown("---")

        for k in bolumler:
            if k in ["deneyim", "egitim"]:
                inputs[k] = st.text_area(
                    f"{p[k]} (Kurum | Tarih | Pozisyon | Açıklama — 2 Enter = yeni blok)"
                )
            elif k in ["projeler"]:
                inputs[k] = st.text_area(
                    f"{p[k]} (Proje Adı | Tarih | Pozisyon | Açıklama — 2 Enter = yeni blok)"
                )
            elif k in ["sertifikalar", "basarilar"]:
                inputs[k] = st.text_area(
                    f"{p[k]} (Başlık | Tarih | Veren Kurum | Açıklama — 2 Enter = yeni blok)"
                )
            else:
                inputs[k] = st.text_area(p[k])

        submitted = st.form_submit_button(p["buton"], use_container_width=True)

# ==============================
# 5. PDF ÜRETİMİ
# ==============================
if submitted and ad:
    pdf = OxfordCV()
    pdf.user_data = {"ad": ad, "email": email, "tel": tel, "adres": adres}
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def isle_blok(text, key):
        if text:
            pdf.bolum_basligi(p[key])
            for blok in text.split("\n\n"):
                if "|" in blok:
                    parca = blok.split("|")
                    while len(parca) < 4:
                        parca.append("")
                    pdf.blok_ekle(
                        parca[0].strip(),
                        parca[1].strip(),
                        parca[2].strip(),
                        parca[3].strip()
                    )

    def isle_sade(text, key):
        if text:
            pdf.bolum_basligi(p[key])
            pdf.set_font(pdf.main_font, "", 9.5)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, text)

    for anahtar in sirali_anahtarlar:
        if anahtar in ["deneyim", "egitim", "projeler", "sertifikalar", "basarilar"]:
            isle_blok(inputs[anahtar], anahtar)
        else:
            isle_sade(inputs[anahtar], anahtar)

    if "referanslar" not in sirali_anahtarlar:
        pdf.bolum_basligi(p["referanslar"])
        pdf.multi_cell(0, 5, "References available upon request.")

    pdf_bytes = bytes(pdf.output())

    with col_preview:
        st.subheader("👀 Önizleme")
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="900"></iframe>',
            unsafe_allow_html=True
        )
        st.download_button(
            f"📥 {p['indir']}",
            data=pdf_bytes,
            file_name="Oxford_ATS_CV.pdf",
            use_container_width=True
        )
