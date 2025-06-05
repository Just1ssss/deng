import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import os
import json
from datetime import datetime

# Custom CSS for better appearance
st.markdown("""
    <style>
    .stForm {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    .stTextInput label, .stNumberInput label {
        color: #333333 !important;
        font-weight: bold;
        font-size: 14px;
    }
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #ced4da !important;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
        font-weight: bold;
        width: 100%;
        padding: 0.5rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .delete-btn {
        background-color: #f44336 !important;
    }
    .delete-btn:hover {
        background-color: #d32f2f !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Firebase
def initialize_firebase():
    try:
        # Check if Firebase key exists
        if not os.path.exists("firebase_key.json"):
            st.error("ไฟล์ firebase_key.json ไม่พบ กรุณาเพิ่มไฟล์ในโฟลเดอร์โปรเจค")
            st.stop()

        # Verify JSON file is valid
        with open("firebase_key.json") as f:
            json.load(f)

        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://home-be9db-default-rtdb.asia-southeast1.firebasedatabase.app/',
                'projectId': 'home-be9db'
            })
        
        return db.reference('friend_houses')
    
    except json.JSONDecodeError:
        st.error("ไฟล์คีย์ไม่ถูกต้อง กรุณาดาวน์โหลดไฟล์ใหม่จาก Firebase Console")
        st.stop()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {str(e)}")
        st.stop()

ref = initialize_firebase()

# Data functions
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

# Web UI
st.set_page_config(layout="wide", page_title="Friend Map App", page_icon="🏠")
st.title("🏠 Friend Locations Map")

# Sidebar for adding new friends
with st.sidebar:
    st.header("Add New Friend Location")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name", placeholder="Enter friend's name")
        col1, col2 = st.columns(2)
        with col1:
            x = st.number_input("X coordinate", min_value=0, max_value=500, step=10, value=250)
        with col2:
            y = st.number_input("Y coordinate", min_value=0, max_value=500, step=10, value=250)

        submitted = st.form_submit_button("➕ Add Location")
        if submitted:
            if not name.strip():
                st.error("Please enter a name")
            else:
                if add_friend(name.strip(), int(x), int(y)):
                    st.success(f"Added {name.strip()} at ({x}, {y})")
                    st.balloons()

# Main content area
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    st.subheader("Friends Location Map")
    data = load_data()

    if data:
        try:
            # Prepare data
            x_coords = [info['x'] for info in data.values()]
            y_coords = [info['y'] for info in data.values()]
            names = [info['name'] for info in data.values()]

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8), facecolor='#f8f9fa')
            fig.set_facecolor('#f8f9fa')

            # Set limits and aspect ratio
            ax.set_xlim(0, 500)
            ax.set_ylim(0, 500)
            ax.set_aspect('equal')

            # Custom grid and ticks
            major_ticks = MultipleLocator(50)
            minor_ticks = MultipleLocator(10)
            ax.xaxis.set_major_locator(major_ticks)
            ax.yaxis.set_major_locator(major_ticks)
            ax.xaxis.set_minor_locator(minor_ticks)
            ax.yaxis.set_minor_locator(minor_ticks)

            # Grid styling
            ax.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.7, color='#cccccc')
            ax.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.5, color='#dddddd')

            # Plot points
            scatter = ax.scatter(
                x_coords, y_coords,
                c='#4285F4',
                s=150,
                edgecolors='white',
                linewidths=1.5,
                alpha=0.9,
                zorder=5
            )

            # Annotate points with clear visibility
            for name, x, y in zip(names, x_coords, y_coords):
                ax.annotate(
                    name,
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 15),
                    ha='center',
                    fontsize=10,
                    weight='bold',
                    color='#000000',
                    bbox=dict(
                        boxstyle='round,pad=0.3',
                        fc='white',
                        ec='none',
                        alpha=0.8
                    )
                )

            # Labels and title
            ax.set_title('Friend Locations Map', pad=20, fontsize=16, weight='bold', color='#333333')
            ax.set_xlabel('X Coordinate', labelpad=10, fontsize=12)
            ax.set_ylabel('Y Coordinate', labelpad=10, fontsize=12)

            # Remove spines
            for spine in ['top', 'right', 'bottom', 'left']:
                ax.spines[spine].set_visible(False)

            st.pyplot(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating map: {str(e)}")
    else:
        st.info("No friend locations yet. Add your first location using the sidebar!")

with col2:
    st.subheader("Current Locations")
    if not data:
        st.info("No friend locations yet")
    else:
        for key, info in data.items():
            with st.container(border=True):
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"**{info['name']}**  \n"
                               f"Coordinates: ({info['x']}, {info['y']})")
                with cols[1]:
                    if st.button("🗑️ Delete", key=f"del_{key}", 
                                help=f"Delete {info['name']}'s location",
                                type="secondary", use_container_width=True):
                        if delete_friend(key):
                            st.success(f"Deleted {info['name']}")
                            st.rerun()
