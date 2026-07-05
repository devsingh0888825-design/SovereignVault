        import streamlit as st
import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('sovereign_vault.db')
    c = conn.cursor()
    # Table ko update kiya hai taaki naye fields aayen
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT, name TEXT, dob TEXT, gender TEXT, password TEXT, p1 REAL, p2 REAL, p3 REAL, p4 REAL)''')
    conn.commit()
    conn.close()

class VaultSystem:
    @staticmethod
    def generate_shards(biometric_id):
        # Yahan calculation sahi ki hai
        s1 = round(biometric_id * 0.20, 2)
        s2 = round(biometric_id * 0.30, 2)
        s3 = round(biometric_id * 0.35, 2)
        s4 = round(biometric_id * 0.15, 2)
        shards = [s1, s2, s3, s4]
        # Password mein decimal hatakar string banayi hai
        password = f"{int(s1*100)}{int(s2*100)}{int(s3*100)}{int(s4*100)}"
        return shards, password

st.title("🛡️ SovereignVault Official")
init_db()

# Sidebar menu for Navigation
menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    name = st.text_input("Name")
    dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    st.camera_input("Take a Face Scan")
    bio_id = st.number_input("Enter Biometric Value", min_value=0.0, format="%.2f")
    
    if st.button("Register"):
        if bio_id > 0:
            user_id = f"{name.lower().replace(' ', '.')}.{phone[-4:]}@sovereignvault.com"
            shards, password = VaultSystem.generate_shards(bio_id)
            
            conn = sqlite3.connect('sovereign_vault.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (user_id, name, str(dob), gender, password, *shards))
            conn.commit()
            conn.close()
            
            st.success("Registered Successfully!")
            st.write(f"**User ID:** {user_id}")
            st.write(f"**Biometric Values:** {shards}")
            st.warning(f"**Your Password:** {password}")
        else:
            st.error("Please enter a valid Biometric Value greater than 0")

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
            
