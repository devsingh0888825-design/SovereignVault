import streamlit as st
import sqlite3
import datetime
import os
import cv2
import numpy as np
import mediapipe as mp

# OpenCV environment fix for headless server
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

# Database Setup
def init_db():
    conn = sqlite3.connect('sovereign_vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id TEXT, name TEXT, dob TEXT, gender TEXT, password TEXT, p1 REAL, p2 REAL, p3 REAL, p4 REAL)''')
    conn.commit()
    conn.close()

# Session State Setup
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'reg_data' not in st.session_state:
    st.session_state.reg_data = {}

st.set_page_config(page_title="SovereignVault")
st.title("🛡️ SovereignVault Official")
init_db()

menu = ["Register", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    # Step 1: Personal Details
    if st.session_state.step == 1:
        st.subheader("Step 1: Personal Details")
        name = st.text_input("Name")
        dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        phone = st.text_input("Phone Number")
        
        if st.button("Next"):
            if name and phone:
                st.session_state.reg_data = {'name': name, 'dob': str(dob), 'gender': gender, 'phone': phone}
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please fill Name and Phone Number")

    # Step 2: Face Scan
    elif st.session_state.step == 2:
        st.subheader("Step 2: Face Scan")
        img_file = st.camera_input("Take a Face Scan")
        
        if img_file:
            if st.button("Complete Registration"):
                try:
                    nparr = np.frombuffer(img_file.getvalue(), np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if img is None:
                        st.error("Image capture nahi ho payi, phir se koshish karein.")
                        st.stop()
                        
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    # MediaPipe FaceMesh usage
                    with mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as mesh:
                        results = mesh.process(img_rgb)
                        if results.multi_face_landmarks:
                            lm = results.multi_face_landmarks[0].landmark
                            bio_id = round((abs(lm[159].x - lm[386].x) + abs(lm[1].y - lm[159].y)) * 10000, 2)
                            
                            s1, s2, s3, s4 = bio_id*0.20, bio_id*0.30, bio_id*0.35, bio_id*0.15
                            password = f"{int(s1*100)}{int(s2*100)}{int(s3*100)}{int(s4*100)}"
                            
                            data = st.session_state.reg_data
                            user_id = f"{data['name'].lower().replace(' ', '.')}.{data['phone'][-4:]}@sovereignvault.com"
                            
                            conn = sqlite3.connect('sovereign_vault.db')
                            c = conn.cursor()
                            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                      (user_id, data['name'], data['dob'], data['gender'], password, s1, s2, s3, s4))
                            conn.commit()
                            conn.close()
                            
                            st.session_state.final_id = user_id
                            st.session_state.final_pass = password
                            st.session_state.step = 3
                            st.rerun()
                        else:
                            st.error("Face detect nahi hua, acche se roshni mein scan karein!")
                except Exception as e:
                    st.error(f"Processing Error: {e}")

    # Step 3: Success
    elif st.session_state.step == 3:
        st.success("Registration Successful!")
        st.write(f"**User ID:** {st.session_state.final_id}")
        st.warning(f"**Generated Password:** {st.session_state.final_pass}")
        if st.button("New Registration"):
            st.session_state.step = 1
            st.rerun()

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
                            
