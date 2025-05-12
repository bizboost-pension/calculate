import streamlit as st
import datetime
import json
from PIL import Image
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Υπολογισμός Σύνταξης - The Bizboost", layout="centered")

# --- Branding ---
col_logo, col_title = st.columns([1, 3])
with col_logo:
    logo = Image.open("logo.png")
    st.image(logo, width=100)

with col_title:
    st.title("The Bizboost by G. Dionysiou")
    st.caption("Γραφείο Οικονομικών Συμβουλών | Οικονομολόγος B.A., MSc")

st.markdown("---")

# --- Φόρτωση JSON Αρχείου ---
with st.expander("📂 Φόρτωση JSON από Syntaksi.com"):
    uploaded_file = st.file_uploader("Επιλέξτε αρχείο JSON", type="json")
    data = {}
    if uploaded_file:
        data = json.load(uploaded_file)
        st.success("✅ Φορτώθηκαν δεδομένα από: " + data.get("onoma", {}).get("value", ""))

# --- Εισαγωγή email για αποστολή PDF ---
st.text_input("✉️ Email πελάτη (προαιρετικά για αποστολή PDF)", key="client_email")

# --- Πίνακας ιστορικού υπολογισμών ---
if "log" not in st.session_state:
    st.session_state["log"] = []

# Προεπιλεγμένες τιμές
default_tameio = data.get("tameio", {}).get("value", "ΙΚΑ")
raw_eti = data.get("eti_ellada", {}).get("value", 0)
default_eti = float(raw_eti) if isinstance(raw_eti, (int, float, str)) and str(raw_eti).replace('.', '', 1).isdigit() else 0.0
default_misthos = data.get("misthos_auto_senariou", {}).get("value", 1000.0)
year_birth = data.get("year_birth", {}).get("value", 1960)
ilikia_json = datetime.datetime.now().year - year_birth

# Είσοδοι χρήστη
st.header("🔍 Στοιχεία Ασφαλισμένου")
col1, col2 = st.columns(2)
with col1:
    tameio = st.selectbox("Ασφαλιστικό Ταμείο", ["ΙΚΑ", "ΤΕΒΕ", "ΟΓΑ"], index=["ΙΚΑ", "ΤΕΒΕ", "ΟΓΑ"].index(default_tameio))
    eidiki = st.selectbox("Ειδική Κατηγορία", ["Καμία", "Μητέρα ανηλίκου", "Βαρέα", "Αναπηρική"])
    ilikia = st.number_input("Ηλικία", min_value=18, max_value=100, value=ilikia_json)

with col2:
    ethi_asfalisis = st.number_input("Έτη Πραγματικής Ασφάλισης", min_value=0.0, step=0.5, value=default_eti)
    misthos = st.number_input("Μηνιαίος Μισθός / Εισφορά (EUR)", min_value=0.0, value=default_misthos, step=50.0)

# --- Πολλαπλά Σενάρια Σύνταξης ---
st.markdown("---")
st.subheader("📑 Σενάρια Υπολογισμού με διαφορετικά Πλασματικά Έτη")
scenarios = [0, 1, 2, 3, 4, 5]
results = []

def υπολογισμός(ethi, plasmatika, misthos):
    synolo = ethi + plasmatika
    ethniki = 413
    apodotiki = synolo * misthos * 0.009
    pliris = ethniki + apodotiki
    meiomeni = pliris - 115 if tameio == "ΙΚΑ" and eidiki != "Αναπηρική" else None
    kostos = plasmatika * misthos * (0.16 if tameio == "ΙΚΑ" else 0.20 if tameio == "ΤΕΒΕ" else 0.12) * 12
    return synolo, pliris, meiomeni, kostos

for p in scenarios:
    synolo, pliris, meiomeni, kostos = υπολογισμός(ethi_asfalisis, p, misthos)
    results.append({
        "Πλασματικά Έτη": p,
        "Συνολικά Έτη": synolo,
        "Πλήρης Σύνταξη (EUR)": round(pliris, 2),
        "Μειωμένη Σύνταξη (EUR)": round(meiomeni, 2) if meiomeni else '-',
        "Κόστος Εξαγοράς (EUR)": round(kostos, 2)
    })

st.table(results)

# --- Εξαγωγή PDF ---
if st.button("📄 Λήψη Αναφοράς σε PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "The Bizboost by G. Dionysiou", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, "Αναφορά Υπολογισμού Σύνταξης", ln=True, align='C')
    pdf.ln(10)

    report_data = [
        ("Ασφαλιστικό Ταμείο", tameio),
        ("Ειδική Κατηγορία", eidiki),
        ("Ηλικία", ilikia),
        ("Πραγματικά Έτη", ethi_asfalisis),
        ("Μηνιαίος Μισθός", f"{misthos:.2f} EUR")
    ]

    for row in results:
        if row["Πλασματικά Έτη"] == 2:
            report_data += [
                ("Πλασματικά Έτη", row["Πλασματικά Έτη"]),
                ("Συνολικά Έτη", row["Συνολικά Έτη"]),
                ("Πλήρης Σύνταξη (EUR)", row["Πλήρης Σύνταξη (EUR)"]),
                ("Μειωμένη Σύνταξη (EUR)", row["Μειωμένη Σύνταξη (EUR)"]),
                ("Κόστος Εξαγοράς (EUR)", row["Κόστος Εξαγοράς (EUR)"])
            ]
            break

    pdf.set_font("Arial", '', 11)
    for label, value in report_data:
        pdf.cell(70, 8, f"{label}:", border=0)
        pdf.cell(0, 8, str(value), ln=True, border=0)

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 10, "© 2025 The Bizboost by G. Dionysiou", align='C')

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    with open(tmp_file.name, "rb") as f:
        st.download_button("⬇️ Κατεβάστε την Αναφορά PDF", f, file_name="Syntaksi_Report_Bizboost.pdf")

# Footer
st.markdown("---")
st.markdown("<center><sub>© 2025 The Bizboost by G. Dionysiou | All rights reserved.</sub></center>", unsafe_allow_html=True)
