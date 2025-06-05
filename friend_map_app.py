import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib import rcParams

# ตั้งค่าฟอนต์สำหรับ Matplotlib เพื่อรองรับภาษาไทย
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma', 'DejaVu Sans', 'Lucida Grande', 'Verdana']

# --- Firebase init ---
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://home-be9db-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    ref = db.reference('friend_houses')
except Exception as e:
    st.error(f"การเชื่อมต่อ Firebase ล้มเหลว: {str(e)}")
    st.stop()


# --- Data functions ---
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


# --- Web UI ---
st.set_page_config(layout="wide", page_title="แผนที่บ้านเพื่อน", page_icon="🏠")
st.title("🏠 แผนที่บ้านเพื่อน")

# Custom CSS for better appearance
st.markdown("""
    <style>
    /* Main form styling */
    .stForm {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }

    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #333333 !important;
        font-weight: bold;
        font-size: 14px;
    }

    /* Input fields */
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #ced4da !important;
    }

    /* Button styling */
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

    /* Delete button */
    .delete-btn {
        background-color: #f44336 !important;
    }

    .delete-btn:hover {
        background-color: #d32f2f !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #37474f;
        padding: 20px;
        border-right: 1px solid #e0e0e0;
    }

    /* Container styling */
    .stContainer {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #ffffff;
    }

    /* Success message */
    .stAlert {
        border-radius: 8px;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .stForm {
            padding: 15px;
        }
        [data-testid="stSidebar"] {
            padding: 15px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for adding new friends
with st.sidebar:
    st.header("เพิ่มบ้านเพื่อนใหม่")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("ชื่อ", placeholder="ใส่ชื่อเพื่อน")
        col1, col2 = st.columns(2)
        with col1:
            x = st.number_input("ตำแหน่ง X", min_value=0, max_value=500, step=10, value=250)
        with col2:
            y = st.number_input("ตำแหน่ง Y", min_value=0, max_value=500, step=10, value=250)

        submitted = st.form_submit_button("➕ เพิ่มตำแหน่ง")
        if submitted:
            if not name.strip():
                st.error("กรุณากรอกชื่อเพื่อน")
            else:
                if add_friend(name.strip(), int(x), int(y)):
                    st.success(f"เพิ่ม {name.strip()} ที่ตำแหน่ง ({x}, {y}) สำเร็จแล้ว!")
                    st.balloons()

# Main content area
col1, col2 = st.columns([2, 1], gap="medium")

# ... (keep all previous imports and Firebase setup code unchanged until the plotting section)

with col1:
    st.subheader("Friend Locations Map")
    data = load_data()

    if data:
        try:
            # Prepare data
            x_coords = [info['x'] for info in data.values()]
            y_coords = [info['y'] for info in data.values()]
            names = [info['name'] for info in data.values()]

            # Create figure with better styling
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

            # Plot points with better styling
            scatter = ax.scatter(
                x_coords, y_coords,
                c='#4285F4',
                s=40,
                edgecolors='white',
                linewidths=1.5,
                alpha=0.9,
                zorder=5
            )

            # Annotate points with improved visibility
            for name, x, y in zip(names, x_coords, y_coords):
                ax.annotate(
                    name,
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 15),  # Increased offset
                    ha='center',
                    fontsize=10,
                    weight='bold',
                    color='#000000',  # Changed to pure black
                    bbox=dict(  # Added background box
                        boxstyle='round,pad=0.3',
                        fc='white',  # White background
                        ec='none',  # No edge
                        alpha=0.8  # Slightly transparent
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
    st.subheader("รายชื่อและตำแหน่ง")
    if not data:
        st.info("ยังไม่มีข้อมูลบ้านเพื่อน")
    else:
        for key, info in data.items():
            with st.container(border=True):
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"**{info['name']}**  \n"
                                f"ตำแหน่ง: ({info['x']}, {info['y']})")
                with cols[1]:
                    if st.button("🗑️ ลบ", key=f"del_{key}", help=f"ลบตำแหน่งของ {info['name']}",
                               type="secondary", use_container_width=True,
                               kwargs={"class": "delete-btn"}):
                        if delete_friend(key):
                            st.success(f"ลบ {info['name']} สำเร็จแล้ว!")
                            st.rerun()