import streamlit as st
import sqlite3

# Database Setup
def init_db():
    conn = sqlite3.connect('sovereign_vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT, name TEXT, dob TEXT, gender TEXT, password TEXT, p1 REAL, p2 REAL, p3 REAL, p4 REAL)''')
    conn.commit()
    conn.close()

# Logic Engine: Password shards 20%, 30%, 35%, 15%
class VaultSystem:
    @staticmethod
    def generate_shards(biometric_id):
        shards = [round(biometric_id * 0.20, 2), round(biometric_id * 0.30, 2), 
                  round(biometric_id * 0.35, 2), round(biometric_id * 0.15, 2)]
        password = "".join([str(s).replace('.', '') for s in shards])
        return shards, password

st.title("🛡️ SovereignVault Official")
init_db()

menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    name = st.text_input("Name")
    dob = st.date_input("Date of Birth")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    img_file = st.camera_input("Take a Face Scan")
    bio_id = st.number_input("Enter Biometric Value", min_value=0.0)
    
    if st.button("Register"):
        user_id = f"{name.lower()}.{phone[-4:]}@sovereignvault.com"
        shards, password = VaultSystem.generate_shards(bio_id)
        
        conn = sqlite3.connect('sovereign_vault.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  (user_id, name, str(dob), gender, password, *shards))
        conn.commit()
        conn.close()
        # Yahan user ko ID aur Password mil jayega
        st.success(f"Registered Successfully!")
        st.info(f"Your ID: {user_id}")
        st.warning(f"Your Generated Password: {password}")

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
            st.success("Login Successful! Welcome to the Vault.")
        else:
            st.error("Invalid ID or Password")
            
