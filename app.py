import streamlit as st
import sqlite3

# Database Setup
def init_db():
    conn = sqlite3.connect('sovereign_vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT, name TEXT, p1 REAL, p2 REAL, p3 REAL, p4 REAL)''')
    conn.commit()
    conn.close()

# Logic Engine
class VaultSystem:
    @staticmethod
    def generate_shards(biometric_id):
        return [round(biometric_id * 0.20, 2), round(biometric_id * 0.30, 2), 
                round(biometric_id * 0.35, 2), round(biometric_id * 0.15, 2)]

# --- Streamlit UI ---
st.title("🛡️ SovereignVault Official")
init_db()

menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    name = st.text_input("Name")
    phone = st.text_input("Phone Number")
    bio_id = st.number_input("Biometric Scan Value", min_value=0.0)
    
    if st.button("Register"):
        user_id = f"{name.lower()}.{phone[-4:]}@sovereignvault.com"
        shards = VaultSystem.generate_shards(bio_id)
        
        conn = sqlite3.connect('sovereign_vault.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (user_id, name, *shards))
        conn.commit()
        conn.close()
        st.success(f"Registered! Your ID: {user_id}")

elif choice == "Login":
    user_id = st.text_input("User ID")
    bio_id = st.number_input("Biometric Scan Value", min_value=0.0)
    
    if st.button("Login"):
        # Yahan login logic aayega jo database se match karega
        st.write("Verifying...")
        st.info("System Ready for Authentication")
  
