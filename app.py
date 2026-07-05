import streamlit as st
import sqlite3
import datetime
import numpy as np

# OpenCV aur Mediapipe ka error-proof loading
try:
    import cv2
    import mediapipe as mp
    from mediapipe.python.solutions import face_mesh as mp_face_mesh
except ImportError:
    st.error("System libraries load ho rahi hain... page ko 5 seconds mein refresh karein.")
    st.stop()

# Database Setup
def init_db():
    conn = sqlite3.connect('sovereign_vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT, name TEXT, dob TEXT, gender TEXT, password TEXT, p1 REAL, p2 REAL, p3 REAL, p4 REAL)''')
    conn.commit()
    conn.close()

# Face Geometry Logic
def calculate_biometric(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Direct reference to FaceMesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as mesh:
        results = mesh.process(img_rgb)
        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            # Landmark 159 (Left Eye), 386 (Right Eye), aur 1 (Nose Tip)
            eye_dist = abs(lm[159].x - lm[386].x)
            nose_to_eye = abs(lm[1].y - lm[159].y)
            return round((eye_dist + nose_to_eye) * 10000, 2)
    return 0.0

class VaultSystem:
    @staticmethod
    def generate_shards(biometric_id):
        s1, s2, s3, s4 = biometric_id*0.2, biometric_id*0.3, biometric_id*0.35, biometric_id*0.15
        password = f"{int(s1*100)}{int(s2*100)}{int(s3*100)}{int(s4*100)}"
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
    img_file = st.camera_input("Take a Face Scan")
    
    if st.button("Register"):
        if img_file:
            bio_id = calculate_biometric(img_file.getvalue())
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
                st.write(f"**ID:** {user_id}")
                st.warning(f"**Password:** {password}")
            else:
                st.error("Face geometry detect nahi hui, phir se koshish karein!")
        else:
            st.error("Photo kheecho!")

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
                
