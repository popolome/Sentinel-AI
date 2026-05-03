import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image
from detection import analyze_frame
from database import init_db, save_session, get_all_sessions

# This is the Page Config
st.set_page_config(
  page_title="Sentinel AI",
  page_icon="🎯",
  layout="wide"
)

# This initializes the DB
init_db()

# This is the Session State
if "monitoring" not in st.session_state:
  st.session_state.monitoring = False
if "start_time" not in st.session_state:
  st.session_state.start_time = None
if "phone_seconds" not in st.session_state:
  st.session_state.phone_seconds = 0
if "absent_seconds" not in st.session_state:
  st.session_state.absent_seconds = 0
if "social_seconds" not in st.session_state:
  st.session_state.social_seconds = 0
if "focus_score" not in st.session_state:
  st.session_state.focus_score = 100

# This is the Header
st.title("🎯 Sentinel AI")
st.caption("Real-time deep work monitor powered by Computer Vision")

# This is a Two Columns Layout
col1, col2 = st.columns([2, 1])

with col1:
  st.subheader("📷 Live Monitor")

  # This is the Camera Input - Snapshot Mode
  camera_image = st.camera_input(
    "Point your camera at your desk",
    disabled=not st.session_state.monitoring
  )

  # This is the Start / Stop buttons
  btn_col1, btn_col2 = st.columns(2)
  with btn_col1:
    if st.button("▶ Start Session", disabled=st.session_state.monitoring):
      st.session_state.monitoring = True
      st.session_state.start_time = time.time()
      st.session_state.phone_seconds = 0
      st.session_state.absent_seconds = 0
      st.session_state.social_seconds = 0
      st.session_state.focus_score = 100
      st.rerun()

  with btn_col2:
    if st.button("⏹ Stop Session", disabled=not st.session_state.monitoring):
      st.session_state.monitoring = False
      duration = int(time.time() - st.session_state.start_time)
      save_session(
        duration_seconds=duration,
        focus_score=st.session_state.focus_score,
        phone_seconds=st.session_state.phone_seconds,
        absent_seconds=st.session_state.absent_seconds,
        social_seconds=st.session_state.social_seconds
      )
      st.success(f"session saved! Final Focus Score: {st.session_state.focus_score}%")
      st.rerun()

  # This will run inference on each snapshot
  if camera_image and st.session_state.monitoring:
    img_array = np.array(Image.open(camera_image))
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    result = analyze_frame(img_bgr)
  
    # This will update the distraction counters
    if result["distraction_type"] == "phone":
      st.session_state.phone_seconds += 1
    elif result["distraction_type"] == "absent":
      st.session_state.absent_seconds += 1
    elif result["distraction_type"] == "social":
      st.session_state.social_seconds += 1

    # This will recalculate the focus score
    elapsed = max(1, int(time.time() - st.session_state.start_time))
    total_distracted = (
      st.session_state.phone_seconds +
      st.session_state.absent_seconds +
      st.session_state.social_seconds
    )
    st.session_state.focus_score = max(0, int(((elapsed - total_distracted) / elapsed) * 100))
  
    # This will display the annotated frame
    annotated_rgb = cv2.cvtColor(result["annotated_frame"], cv2.COLOR_BGR2RGB)
    st.image(annotated_rgb, caption=result["status"], use_container_width=True)

with col2:
  st.subheader("📊 Live Stats")

  # This is the Focus score Guage
  score = st.session_state.focus_score
  color = "green" if score >= 70 else "orange" if score >= 40 else "red"
  st.markdown(f"""
    <div style='text-align:center; padding: 20px; border-radius: 12px; background: #111;'>
      <p style='color: gray; margin:0;'>Focus Score</p>
      <h1 style='color: {color}; font-size: 64px; margin: 0;'>{score}%</h1>
    </div>
  """, unsafe_allow_html=True)

  st.markdown("---")

  # This is the Distraction Breakdown
  st.markdown("**Distraction Breakdown**")
  st.markdown(f"📱 Phone: `{st.session_state.phone_seconds}s`")
  st.markdown(f"🪑 Absent: `{st.session_state.absent_seconds}s`")
  st.markdown(f"👥 Social: `{st.session_state.social_seconds}s`")

  if st.session_state.start_time:
    elapsed = int(time.time() - st.session_state.start_time)
    st.markdown(f"⏱ Elapsed: `{elapsed}s`")

# This is the Session History
st.markdown("---")
st.subheader("📈 Session History")

sessions = get_all_sessions()

if sessions:
  import pandas as pd
  df = pd.DataFrame(sessions, columns=[
    "Date", "Focus Score", "Duration (s)",
    "Phone (s)", "Absent (s)", "Social (s)"
  ])
  st.line_chart(df.set_index("Date")["Focus Score"])
  st.dataframe(df, use_container_width=True)
else:
  st.info("No sessions yet. Start your first session above!")
