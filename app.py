import streamlit as st
import datetime
from PIL import Image

st.set_page_config(page_title="Υπολογισμός Σύνταξης - The Bizboost", layout="centered")

# --- Branding ---
col_logo, col_title = st.columns([1, 3])
with col_logo:
    logo = Image.open("logo.png")  # προσθέτεις το logo.png στο ίδιο φάκελο
    st.image(logo, width=100)

with col_title:
    st.title("The Bizboost by G. Dionysiou")
    st.caption("Γραφείο Οικονομικών Συμβουλών | Οικονομολόγος B.A., MSc")

st.markdown("---")

# Είσοδοι χρήστη
st.header("🔍 Στοιχεία Ασφαλισμένου")
col1, col2 = st.columns(2)
with col1:
    tameio = st.selectbox("Ασφαλιστικό Ταμείο", ["ΙΚΑ", "ΤΕΒΕ", "ΟΓΑ"])
    eidiki = st.selectbox("Ειδική Κατηγορία", ["Καμία", "Μητέρα ανηλίκου", "Βαρέα", "Αναπηρική"])
    ilikia = st.number_input("Ηλικία", min_value=18, max_value=100, value=60)

with col2:
    ethi_asfalisis = st.number_input("Έτη Πραγματικής Ασφάλισης", min_value=0.0, step=0.5)
    plasmatika = st.number_input("Πλασματικά Έτη", min_value=0.0, step=0.5)
    misthos = st.number_input("Μηνιαίος Μισθός / Εισφορά (€)", min_value=0.0, value=1000.0, step=50.0)

# Υπολογισμοί
synolika_eti = ethi_asfalisis + plasmatika

# Όρια ηλικίας
def orio_ilikias_pliris():
    if eidiki == "Αναπηρική": return 50
    if eidiki == "Μητέρα ανηλίκου": return 55
    if eidiki == "Βαρέα": return 62
    return 67

def orio_ilikias_meiomenis():
    if eidiki == "Αναπηρική": return 50
    if eidiki == "Βαρέα": return 60
    if tameio == "ΙΚΑ": return 62
    return None

ethniki = 413
syntaxi_pliris = ethniki + (synolika_eti * misthos * 0.009)
syntaxi_meiomeni = syntaxi_pliris - 115 if tameio == "ΙΚΑ" and orio_ilikias_meiomenis() is not None else None

# Κόστος εξαγοράς
kostos_p = 0.16 if tameio == "ΙΚΑ" else 0.20 if tameio == "ΤΕΒΕ" else 0.12
kostos_exagoras = plasmatika * misthos * kostos_p * 12

# Υπολειπόμενα έτη
etoi_pliris = max(0, 15 - synolika_eti)
etoi_meiomenis = max(0, 15 - synolika_eti) if orio_ilikias_meiomenis() else None
etos_syntaxiodotisis = datetime.datetime.now().year + max(0, orio_ilikias_pliris() - ilikia)

# --- Αποτελέσματα ---
st.markdown("---")
st.header("📊 Αποτελέσματα Υπολογισμού")
col1, col2 = st.columns(2)
with col1:
    st.metric("Συνολικά Έτη Ασφάλισης", f"{synolika_eti:.1f} έτη")
    st.metric("Υπολειπόμενα για Πλήρη", f"{etoi_pliris:.1f} έτη")
    if etoi_meiomenis is not None:
        st.metric("Υπολειπόμενα για Μειωμένη", f"{etoi_meiomenis:.1f} έτη")
    st.metric("Έτος Πλήρους Σύνταξης", f"{etos_syntaxiodotisis}")

with col2:
    st.metric("Πλήρης Σύνταξη (€)", f"{syntaxi_pliris:.0f}")
    if syntaxi_meiomeni:
        st.metric("Μειωμένη Σύνταξη (€)", f"{syntaxi_meiomeni:.0f}")
    st.metric("Κόστος Εξαγοράς (€)", f"{kostos_exagoras:.0f}")

# Πρόταση
st.markdown("---")
if synolika_eti >= 15 and ilikia >= orio_ilikias_pliris():
    st.success("✅ Μπορείτε να υποβάλετε αίτηση για πλήρη σύνταξη.")
elif syntaxi_meiomeni and synolika_eti >= 15 and ilikia >= orio_ilikias_meiomenis():
    st.info("ℹ️ Μπορείτε να εξετάσετε μειωμένη σύνταξη.")
else:
    st.warning(f"⚠️ Απαιτούνται ακόμα {etoi_pliris:.1f} έτη ασφάλισης ή ηλικία.")

# Footer
st.markdown("---")
st.markdown("<center><sub>© 2025 The Bizboost by G. Dionysiou | All rights reserved.</sub></center>", unsafe_allow_html=True)
