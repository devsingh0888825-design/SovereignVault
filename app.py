import streamlit as st
import sqlite3

# Database Setup (DOB aur Gender add kiya hai)
def init_db():
    conn = sqlite3.connect('sovereign_vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT, name TEXT, dob TEXT, gender TEXT, p1 REAL, p2 REAL, p3 REAL, p4 REAL)''')
    conn.commit()
    conn.close()

class VaultSystem:
    @staticmethod
    def generate_shards(biometric_id):
        return [round(biometric_id * 0.20, 2), round(biometric_id * 0.30, 2), 
                round(biometric_id * 0.35, 2), round(biometric_id * 0.15, 2)]

st.title("🛡️ SovereignVault Official")
init_db()

menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    name = st.text_input("Name")
    dob = st.date_input("Date of Birth")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    
    # Face Scan (Camera Input)
    st.write("---")
    st.subheader("Biometric Face Scan")
    img_file = st.camera_input("Take a Face Scan")
    
    bio_id = st.number_input("Enter Manual Biometric Value (if camera fails)", min_value=0.0)
    
    if st.button("Register"):
        user_id = f"{name.lower()}.{phone[-4:]}@sovereignvault.com"
        shards = VaultSystem.generate_shards(bio_id)
        
        conn = sqlite3.connect('sovereign_vault.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                  (user_id, name, str(dob), gender, *shards))
        conn.commit()
        conn.close()
        st.success(f"Registered! Your ID: {user_id}")

elif choice == "Login":
    user_id = st.text_input("User ID")
    img_login = st.camera_input("Login Face Scan")
    bio_id = st.number_input("Manual Biometric Value", min_value=0.0)
    
    if st.button("Login"):
        st.write("Verifying...")
        
