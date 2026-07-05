import streamlit as st
import sqlite3
import datetime

# Database Setup
def init_db():
    conn = sqlite3.connect('sovereign_vault.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT, name TEXT, dob TEXT, gender TEXT, password TEXT, p1 REAL, p2 REAL, p3 REAL, p4 REAL)''')
    conn.commit()
    conn.close()

class VaultSystem:
    @staticmethod
    def generate_shards(biometric_id):
        # Biometric id ko 1000 se divide karke normalise kar rahe hain
        val = float(biometric_id) / 100000 
        s1, s2, s3, s4 = val*0.2, val*0.3, val*0.35, val*0.15
        password = f"{int(s1*100000)}{int(s2*100000)}{int(s3*100000)}{int(s4*100000)}"
        return [s1, s2, s3, s4], password

st.title("🛡️ SovereignVault Official")
init_db()

menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    name = st.text_input("Name")
    dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    
    # Camera se photo lo
    img_file = st.camera_input("Take a Face Scan")
    
    if st.button("Register"):
        if img_file:
            # JUGAAD: Photo ki size (bytes) ko hi biometric value maan lo
            bio_id = len(img_file.getvalue()) 
            user_id = f"{name.lower().replace(' ', '.')}.{phone[-4:]}@sovereignvault.com"
            shards, password = VaultSystem.generate_shards(bio_id)
            
            conn = sqlite3.connect('sovereign_vault.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (user_id, name, str(dob), gender, password, *shards))
            conn.commit()
            conn.close()
            st.success("Registered Successfully!")
            st.warning(f"Your Generated Password: {password}")
        else:
            st.error("Pehle photo kheecho!")

elif choice == "Login":
    st.subheader("Login Portal")
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        conn = sqlite3.connect('sovereign_vault.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ? AND password = ?", (user_id, password))
        data = c.fetchone()
        conn.close()
        if data:
            st.success(f"Welcome back, {data[1]}!")
        else:
            st.error("Invalid ID or Password")
            
