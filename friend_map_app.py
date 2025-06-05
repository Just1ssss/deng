import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime

# ตั้งค่าหน้าก่อนนำเข้า Firebase
st.set_page_config(layout="wide", page_title="Friend Map App", page_icon="🏠")

# Custom CSS ที่แก้ไขแล้ว
st.markdown("""
<style>
.stForm {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    margin-bottom: 20px;
}
.stTextInput input, .stNumberInput input {
    background-color: #ffffff !important;
    border: 1px solid #ced4da !important;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 4px;
    font-weight: bold;
}
.delete-btn {
    background-color: #f44336 !important;
}
</style>
""", unsafe_allow_html=True)

# ฟังก์ชันเริ่มต้น Firebase ที่แก้ไขแล้ว
def initialize_firebase():
    try:
        # ตรวจสอบก่อนว่า Firebase ยังไม่ถูกเริ่มต้น
        if not firebase_admin._apps:
            # ตรวจสอบไฟล์คีย์
            if not os.path.exists("firebase_key.json"):
                st.error("ไฟล์ firebase_key.json ไม่พบ")
                st.stop()

            # ตรวจสอบว่าไฟล์คีย์ถูกต้อง
            try:
                with open("firebase_key.json") as f:
                    json.load(f)
            except Exception as e:
                st.error(f"ไฟล์คีย์ไม่ถูกต้อง: {str(e)}")
                st.stop()

            # เริ่มต้น Firebase
            try:
                cred = credentials.Certificate("firebase_key.json")
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://home-be9db-default-rtdb.asia-southeast1.firebasedatabase.app/'
                })
            except Exception as e:
                st.error(f"การเชื่อมต่อ Firebase ล้มเหลว: {str(e)}")
                st.stop()

        return db.reference('friend_houses')

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดร้ายแรง: {str(e)}")
        st.stop()

# เริ่มต้น Firebase
try:
    ref = initialize_firebase()
except Exception as e:
    st.error(f"ไม่สามารถเริ่มต้นแอปได้: {str(e)}")
    st.stop()

# ฟังก์ชันจัดการข้อมูล
def load_data():
    try:
        data = ref.get()
        return data or {}
    except Exception as e:
        st.error(f"โหลดข้อมูลไม่สำเร็จ: {str(e)}")
        return {}

def add_friend(name, x, y):
    try:
        new_ref = ref.push()
        new_ref.set({'name': name, 'x': x, 'y': y})
        return True
    except Exception as e:
        st.error(f"เพิ่มข้อมูลไม่สำเร็จ: {str(e)}")
        return False

def delete_friend(key):
    try:
        ref.child(key).delete()
        return True
    except Exception as e:
        st.error(f"ลบข้อมูลไม่สำเร็จ: {str(e)}")
        return False

# ส่วนติดต่อผู้ใช้
st.title("🏠 แผนที่บ้านเพื่อน")

# Sidebar
with st.sidebar:
    st.header("เพิ่มตำแหน่งใหม่")
    with st.form("add_form"):
        name = st.text_input("ชื่อเพื่อน")
        x = st.number_input("ตำแหน่ง X", 0, 500, 250)
        y = st.number_input("ตำแหน่ง Y", 0, 500, 250)

        if st.form_submit_button("เพิ่มตำแหน่ง"):
            if name.strip():
                if add_friend(name.strip(), x, y):
                    st.success("เพิ่มข้อมูลสำเร็จ!")
                    st.rerun()
            else:
                st.warning("กรุณากรอกชื่อเพื่อน")

# แผนที่และรายชื่อ
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("แผนที่ตำแหน่ง")
    data = load_data()

    if data:
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_xlim(0, 500)
            ax.set_ylim(0, 500)
            ax.grid(True)

            # พล็อตจุดและชื่อ
            for key, info in data.items():
                ax.scatter(info['x'], info['y'], color='blue')
                ax.text(info['x'], info['y'] + 15, info['name'],
                        ha='center', fontsize=10,
                        bbox=dict(facecolor='white', alpha=0.7))

            st.pyplot(fig)
        except Exception as e:
            st.error(f"สร้างแผนที่ไม่สำเร็จ: {str(e)}")
    else:
        st.info("ยังไม่มีข้อมูล")

with col2:
    st.subheader("รายชื่อเพื่อน")
    if data:
        for key, info in data.items():
            with st.container(border=True):
                st.write(f"**{info['name']}**")
                st.write(f"ตำแหน่ง: ({info['x']}, {info['y']})")
                if st.button("ลบ", key=key):
                    if delete_friend(key):
                        st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลเพื่อน")
