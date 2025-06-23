import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import matplotlib.pyplot as plt
import os
import json

st.set_page_config(layout="wide", page_title="Friend Map App", page_icon="🏠")

# CSS ตกแต่งสวยงาม
st.markdown("""
<style>
/* รูปแบบฟอร์มเพิ่มข้อมูล */
.stForm {
    background-color: #f0f4f8;
    padding: 20px;
    border-radius: 12px;
    border: 1.5px solid #d1d9e6;
    margin-bottom: 25px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Input สีพื้นและขอบ */
.stTextInput input, .stNumberInput input {
    background-color: #ffffff !important;
    border: 1.8px solid #a3b0d1 !important;
    border-radius: 6px !important;
    padding: 8px !important;
    font-size: 16px !important;
}

/* ปุ่มสีเขียวสดใส */
.stButton>button {
    background-color: #3b82f6;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 18px;
    transition: background-color 0.3s ease;
}

.stButton>button:hover {
    background-color: #2563eb;
}

/* ปุ่มลบสีแดงสด */
.delete-btn, button[key^="delete_"] {
    background-color: #ef4444 !important;
    color: white !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
    font-weight: 600 !important;
    transition: background-color 0.3s ease;
}

.delete-btn:hover, button[key^="delete_"]:hover {
    background-color: #b91c1c !important;
}

/* กล่องรายชื่อเพื่อน */
.friend-container {
    border: 1.5px solid #d1d9e6;
    padding: 15px 18px;
    border-radius: 10px;
    margin-bottom: 12px;
    background-color: #f9fbff;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.15);
}

/* ชื่อเพื่อนใหญ่และโดดเด่น */
.friend-name {
    font-weight: 700;
    font-size: 18px;
    color: #1e3a8a;
    margin-bottom: 6px;
}

/* ตำแหน่งเพื่อนสีเทาอ่อน */
.friend-position {
    font-size: 14px;
    color: #4b5563;
}

/* Title แผนที่ */
h2, h3 {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #1e40af;
}

/* กริดและแกนของแผนที่ */
canvas {
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

def initialize_firebase():
    try:
        if not firebase_admin._apps:
            if not os.path.exists("firebase_key.json"):
                st.error("ไฟล์ firebase_key.json ไม่พบ")
                st.stop()

            try:
                with open("firebase_key.json") as f:
                    json.load(f)
            except Exception as e:
                st.error(f"ไฟล์คีย์ไม่ถูกต้อง: {str(e)}")
                st.stop()

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

try:
    ref = initialize_firebase()
except Exception as e:
    st.error(f"ไม่สามารถเริ่มต้นแอปได้: {str(e)}")
    st.stop()

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

st.title("🏠 แผนที่บ้านเพื่อน")

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
                    st.experimental_rerun()
            else:
                st.warning("กรุณากรอกชื่อเพื่อน")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("แผนที่ตำแหน่ง")
    data = load_data()

    if data:
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_xlim(0, 500)
            ax.set_ylim(0, 500)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_facecolor('#f5f7fa')

            for key, info in data.items():
                ax.scatter(info['x'], info['y'], color='#2563eb', s=100, alpha=0.8)
                ax.text(info['x'], info['y'] + 15, info['name'],
                        ha='center', fontsize=12, fontweight='bold',
                        bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.3'))

            st.pyplot(fig)
        except Exception as e:
            st.error(f"สร้างแผนที่ไม่สำเร็จ: {str(e)}")
    else:
        st.info("ยังไม่มีข้อมูล")

with col2:
    st.subheader("รายชื่อเพื่อน")
    if data:
        for key, info in data.items():
            st.markdown(f"""
            <div class="friend-container">
                <div class="friend-name">{info['name']}</div>
                <div class="friend-position">ตำแหน่ง: ({info['x']}, {info['y']})</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("ลบ", key=f"delete_{key}", help="ลบตำแหน่งนี้"):
                if delete_friend(key):
                    st.experimental_rerun()
    else:
        st.info("ยังไม่มีข้อมูลเพื่อน")
