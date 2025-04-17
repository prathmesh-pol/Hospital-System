# 🏥 Medical Diagnosis & Hospital Booking System

An **AI-powered Streamlit application** that diagnoses diseases based on symptoms and manages hospital bed bookings with real-time availability. This system integrates concepts like **First Order Logic**, **Heuristics**, **Backtracking**, and **Constraint Satisfaction Problems** to simulate intelligent decision-making in a medical setting.

---

## 🚀 Features

- ✅ **Symptom-Based Diagnosis** of 5 diseases: Flu, Food Poisoning, Malaria, Dengue, and Typhoid.
- 🏨 **Real-Time Bed Availability** across 10 hospitals.
- 🙋‍♀️ **User Flow** for hospital selection and booking confirmation.
- 🛠 **Admin Dashboard** to:
  - View bed availability.
  - View and delete patient bookings.
  - Reset beds for all hospitals.

---

## 🤖 AI Concepts Applied

| Concept | Usage |
|--------|-------|
| **First Order Logic** | Used to define diagnosis rules based on combinations of symptoms. |
| **Heuristic** | Selects the first available hospital for a given disease. |
| **Backtracking** | Allows retrying other hospitals if the selected one has no beds. |
| **Constraint Satisfaction** | Ensures hospital bed limits are respected during booking. |

---

## 🧪 Technologies Used

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **Backend Logic**: Python
- **Database**: SQLite (via `sqlite3`)

---

## 🖥 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/hospital-booking-system.git
   cd hospital-booking-system
