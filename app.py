import streamlit as st
import sqlite3

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect("hospital.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS hospitals (
    name TEXT PRIMARY KEY,
    disease TEXT,
    available_beds INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    name TEXT,
    hospital TEXT
)
""")

cursor.execute("SELECT COUNT(*) FROM hospitals")
if cursor.fetchone()[0] == 0:
    hospitals = [
        ("Hospital A", "Flu", 5),
        ("Hospital B", "Flu", 5),
        ("Hospital C", "Food Poisoning", 5),
        ("Hospital D", "Food Poisoning", 5),
        ("Hospital E", "Malaria", 5),
        ("Hospital F", "Malaria", 5),
        ("Hospital G", "Dengue", 5),
        ("Hospital H", "Dengue", 5),
        ("Hospital I", "Typhoid", 5),
        ("Hospital J", "Typhoid", 5),
    ]
    cursor.executemany("INSERT INTO hospitals VALUES (?, ?, ?)", hospitals)
    conn.commit()

# ---------- SESSION STATE ----------
for key in ["diagnosis", "hospital_options", "booking_done", "confirmed_hospital"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "booking_done" else False

# ---------- EXPLANATION SECTION (STATIC) ----------
with st.sidebar:
    st.markdown("### 💡 AI Concepts Used")
    st.info("""
- **First Order Logic (FOL)**: Used to define rules for disease diagnosis based on selected symptoms.
- **Heuristic**: Chooses the first hospital with available beds to speed up booking.
- **Backtracking**: If a chosen hospital has no beds, it tries the next available hospital.
- **Constraint Satisfaction Problem (CSP)**: Ensures that bookings only happen when bed availability constraints are met.
    """)

# ---------- DIAGNOSIS FUNCTION ----------
def diagnose_with_heuristics(symptoms_selected):

    normalized_symptoms = {k.lower(): v for k, v in symptoms_selected.items()}
    
    disease_symptom_map = {
        "Flu": ["fatigue", "body aches"],
        "Food Poisoning": ["nausea", "vomiting", "abdominal pain"],
        "Malaria": ["fever", "headache", "chills"],
        "Dengue": ["fever", "joint pain", "rash"],
        "Typhoid": ["fever", "headache", "loss of appetite"],
    }

    disease_scores = {}
    for disease, required_symptoms in disease_symptom_map.items():
        matched = sum(1 for s in required_symptoms if normalized_symptoms.get(s, False))
        disease_scores[disease] = matched

    best_match = max(disease_scores, key=disease_scores.get)

    if disease_scores[best_match] < 2 :
        return "Unknown"

    return best_match

# ---------- MAIN INTERFACE ----------
st.title("🏥 Medical Diagnosis & Booking System")

mode = st.radio("Select Mode", ["User", "Admin"])

# ---------- USER MODE ----------
if mode == "User":
    st.header("🔍 Symptom Checker")

    symptoms = {
        "fever": st.checkbox("Fever"),
        "headache": st.checkbox("Headache"),
        "chills": st.checkbox("Chills"),
        "loss of appetite": st.checkbox("Loss of Appetite"),
        "fatigue": st.checkbox("Fatigue"),
        "body aches": st.checkbox("Body Aches"),
        "nausea": st.checkbox("Nausea"),
        "vomiting": st.checkbox("Vomiting"),
        "abdominal pain": st.checkbox("Abdominal Pain"),
        "joint pain": st.checkbox("Joint Pain"),
        "rash": st.checkbox("Rash"),

    }

    if st.button("Diagnose") and not st.session_state.booking_done:
        diagnosis = diagnose_with_heuristics(symptoms)
        st.session_state.diagnosis = diagnosis
        st.session_state.booking_done = False
        st.session_state.hospital_options = []

        if diagnosis != "Unknown":
            cursor.execute("SELECT name FROM hospitals WHERE disease = ? AND available_beds > 0", (diagnosis,))
            hospitals = [row[0] for row in cursor.fetchall()]
            st.session_state.hospital_options = hospitals

    if st.session_state.diagnosis:
        st.subheader(f"🩺 Diagnosis: {st.session_state.diagnosis}")

        if st.session_state.diagnosis != "Unknown":
            if st.session_state.hospital_options:
                st.success("🏨 Hospitals with available beds:")
                selected = st.radio("Choose a hospital to book:", st.session_state.hospital_options)
                name = st.text_input("Enter your name to confirm booking")

                if st.button("Confirm Booking") and name:
                    cursor.execute("SELECT available_beds FROM hospitals WHERE name = ?", (selected,))
                    beds = cursor.fetchone()
                    if beds and beds[0] > 0:
                        cursor.execute("UPDATE hospitals SET available_beds = available_beds - 1 WHERE name = ?", (selected,))
                        cursor.execute("INSERT INTO patients VALUES (?, ?)", (name, selected))
                        conn.commit()
                        st.session_state.booking_done = True
                        st.session_state.confirmed_hospital = selected
                        st.rerun()

                    else:
                        st.error("No beds available at the selected hospital. Please choose another.")
            else:
                st.warning("No hospitals currently have beds for your condition. Try again later.")
        else:
            st.warning("Unable to determine disease. Please consult a healthcare professional.")

    if st.session_state.booking_done:
        st.success(f"✅ Thank you! Your bed has been booked at **{st.session_state.confirmed_hospital}**.")
        if st.button("Book Another Slot"):
            for key in ["diagnosis", "hospital_options", "booking_done", "confirmed_hospital"]:
                st.session_state[key] = None if key != "booking_done" else False
            st.rerun()


# ---------- ADMIN MODE ----------
elif mode == "Admin":
    st.header("📊 Admin Dashboard")

    st.subheader("🏨 Hospital Bed Availability")
    cursor.execute("SELECT name, disease, available_beds FROM hospitals")
    data = cursor.fetchall()
    for h in data:
        st.write(f"**{h[0]}** ({h[1]}) → Beds Available: {h[2]}")

    if st.button("🔄 Reset All Beds to 5"):
        cursor.execute("UPDATE hospitals SET available_beds = 5")
        conn.commit()
        st.success("All hospital beds have been reset to 5.")
        st.rerun()


    st.subheader("🧑‍🤝‍🧑 Patient Bookings")
    cursor.execute("SELECT rowid, name, hospital FROM patients")
    patients = cursor.fetchall()
#made with love - prathmesh-pol 
    if patients:
        for p in patients:
            st.write(f"• **{p[1]}** booked at **{p[2]}**")

        st.divider()
        st.markdown("### 🗑 Delete a Patient Booking")

        patient_dict = {f"{p[1]} ({p[2]})": p for p in patients}
        selected_patient = st.selectbox("Select patient to delete", list(patient_dict.keys()))

        if st.button("Delete Booking"):
            rowid, name, hospital = patient_dict[selected_patient]
            cursor.execute("DELETE FROM patients WHERE rowid = ?", (rowid,))
            cursor.execute("UPDATE hospitals SET available_beds = available_beds + 1 WHERE name = ?", (hospital,))
            conn.commit()
            st.success(f"Deleted booking for {name} at {hospital}.")
            st.rerun()

    else:
        st.info("No patient bookings yet.")
