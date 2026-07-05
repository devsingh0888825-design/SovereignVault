import streamlit as st
import sqlite3
import datetime
import cv2
import mediapipe as mp
import numpy as np

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
    
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            eye_dist = abs(landmarks[159].x - landmarks[386].x)
            nose_to_eye = abs(landmarks[1].y - landmarks[159].y)
            dist = (eye_dist + nose_to_eye) * 10000
            return round(dist, 2)
    return 0.0

class VaultSystem:
    @staticmethod
    def generate_shards(biometric_id):
        s1 = round(biometric_id * 0.20, 2)
        s2 = round(biometric_id * 0.30, 2)
        s3 = round(biometric_id * 0.35, 2)
        s4 = round(biometric_id * 0.15, 2)
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
                st.write(f"**Biometric ID:** {bio_id}")
                st.warning(f"**Generated Password:** {password}")
            else:
                st.error("Face scan thik se nahi hua, phir se koshish karein!")
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
            
