import cv2
import time
import os
import threading
import csv
import numpy as np
from datetime import datetime
from ultralytics import YOLO
import pyvirtualcam
import tkinter as tk
from tkinter import ttk
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import shutil
import wave
import struct
import math

# --- OS INTEGRATION & ENTERPRISE IMPORTS ---
import winsound
import ctypes
from plyer import notification
import psutil
import pygetwindow as gw
import pystray
from PIL import Image, ImageDraw
import sqlite3
import hashlib
import logging
from flask import Flask, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

"""
================================================================================
  ENTERPRISE EDGE-AI ZERO-TRUST PRIVACY GUARD (v11.0 - STABILITY & GRACE PERIODS)
================================================================================
"""

def capture_threat_snapshot(frame, threat_label):
    if not os.path.exists("threat_snapshots"):
        os.makedirs("threat_snapshots")
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"threat_snapshots/incident_{threat_label}_{timestamp_str}.jpg"
    cv2.imwrite(filename, frame)

def ensure_alarm_sound():
    if not os.path.exists("security_alarm.wav"):
        sample_rate = 44100
        try:
            with wave.open("security_alarm.wav", "w") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(sample_rate)
                for i in range(int(sample_rate * 0.6)):
                    freq = 1200 if (i // 4000) % 2 == 0 else 1800
                    value = int(16000.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                    f.writeframes(struct.pack('<h', value))
        except Exception:
            pass

ensure_alarm_sound()

# --- MEDIAPIPE FACE LANDMARKER SETUP ---
base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=False,
                                       num_faces=2)
try:
    detector = vision.FaceLandmarker.create_from_options(options)
    FACE_AI_AVAILABLE = True
except Exception:
    FACE_AI_AVAILABLE = False

def calculate_gaze_intent(frame, box):
    if not FACE_AI_AVAILABLE: return 1.0
    x1, y1, x2, y2 = box
    roi = frame[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
    if roi.size == 0: return 1.0

    try:
        rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_roi)
        detection_result = detector.detect(mp_image)

        if detection_result.face_landmarks:
            for face_landmarks in detection_result.face_landmarks:
                nose_tip = face_landmarks[1].x
                left_side = face_landmarks[234].x
                right_side = face_landmarks[454].x
                
                face_width = right_side - left_side
                if face_width <= 0: return 1.0
                
                nose_ratio = (nose_tip - left_side) / face_width
                
                # WIDENED TOLERANCE: Allows natural eye movement without false alarms
                if 0.25 < nose_ratio < 0.75:
                    return 3.0  
                else:
                    return 0.5  
    except Exception:
        pass
    return 1.0

# ---------------------------------------------------------
# 🚨 INSTANT EMAIL-TO-MOBILE PUSH NOTIFICATION CONFIG
# ---------------------------------------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "yaswanthsai5704@gmail.com"
# ⚠️ Paste your 16-digit Google App Password here
SENDER_PASSWORD = "your_password"  
RECIPIENT_EMAIL = "yaswanthsai5704@gmail.com"

def trigger_mobile_alert(alert_type, message):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = f"🚨 EdgeGuard Security Alert: {alert_type}"
        body = f"Critical Security Event Detected:\n\n{message}\n\nEnvironment: Active Protection Protocol Triggered."
        msg.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
    except Exception:
        pass

# --- LOCAL REST API ---
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

api_threat_state = {"status": "SAFE", "latest_threat": None, "timestamp": None}

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"ai_engine_status": ai_status, "security_ledger": api_threat_state})

def run_api():
    app.run(host='127.0.0.1', port=5050, debug=False, use_reloader=False)

# --- CRYPTOGRAPHIC AUDIT LEDGER ---
db_path = "secure_audit_ledger.db"

def init_crypto_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS compliance_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, threat_level TEXT, 
                  object_label TEXT, action TEXT, prev_hash TEXT, current_hash TEXT)''')
    conn.commit()
    conn.close()

def get_last_hash():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT current_hash FROM compliance_logs ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    return row[0] if row else "GENESIS_HASH"

init_crypto_db()
audit_log_path = f"compliance_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
with open(audit_log_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Threat Level", "Object Redacted", "Action Taken"])

def log_incident(threat_level, object_label, action="Sub-Sampling Redaction"):
    global api_threat_state
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(audit_log_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, threat_level, object_label, action])
        
    prev_hash = get_last_hash()
    raw_data = f"{timestamp}{threat_level}{object_label}{action}{prev_hash}"
    current_hash = hashlib.sha256(raw_data.encode()).hexdigest()
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO compliance_logs (timestamp, threat_level, object_label, action, prev_hash, current_hash)
                 VALUES (?, ?, ?, ?, ?, ?)''', (timestamp, threat_level, object_label, action, prev_hash, current_hash))
    conn.commit()
    conn.close()
    api_threat_state = {"status": "THREAT_DETECTED", "latest_threat": object_label, "timestamp": timestamp}

# --- AI CORE ENGINE ---
class EdgeAIEngine:
    def __init__(self, model_name="yolo26n", target_width=640, target_height=640):
        self.model_name = model_name
        self.pt_path = f"{model_name}.pt"
        self.onnx_path = f"{model_name}.onnx"
        self.img_size = (target_width, target_height)
        self.active_classes = [0, 26, 63, 67, 73] 
        self._prepare_model()

    def _prepare_model(self):
        if not os.path.exists(self.onnx_path):
            model = YOLO(self.pt_path)
            model.export(format="onnx", imgsz=self.img_size[0])
        self.model = YOLO(self.onnx_path, task="detect")

    def process_frame(self, frame):
        results = self.model(frame, conf=0.35, verbose=False, imgsz=640)
        detected_objects = []
        if results and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                cls_id = int(box.cls[0].item())
                if cls_id in self.active_classes:
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    label = self.model.names[cls_id]
                    area = (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])
                    detected_objects.append({"box": xyxy, "label": label, "class_id": cls_id, "area": area})
        return detected_objects

def purge_clipboard():
    try:
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
    except Exception:
        pass

latest_frame = None
latest_ai_frame = None
cached_detections = []
running = True
full_privacy_override = False
frame_lock = threading.Lock()
profile_string = "Public Cafe Mode"
ai_status = "INITIALIZING..."

def enhance_low_light(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if np.mean(gray) < 80:
        gamma = 1.5
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(frame, table)
    return frame

# --- ECO-STANDBY THREAD ---
def bg_inference_worker(ai_engine):
    global latest_ai_frame, cached_detections, running, ai_status
    prev_gray = None
    while running:
        if latest_ai_frame is not None:
            with frame_lock:
                frame_to_process = latest_ai_frame.copy()
            
            gray = cv2.cvtColor(frame_to_process, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            run_ai = True
            if prev_gray is not None:
                frame_delta = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                if np.sum(thresh) < 15000: 
                    if int(time.time() * 10) % 3 != 0:
                        run_ai = False
            prev_gray = gray
            
            if run_ai:
                fresh_detections = ai_engine.process_frame(frame_to_process)
                with frame_lock:
                    cached_detections = fresh_detections
                    ai_status = "AI ENGINE: COMPUTING"
            else:
                with frame_lock:
                    ai_status = "AI ENGINE: ECO-STANDBY"
        time.sleep(0.01)

# --- 3D SPATIAL RADAR HUD ---
radar_angle = 0.0
def draw_spatial_radar(frame, primary_user_box, bystanders, gadgets):
    global radar_angle
    h, w, _ = frame.shape
    center_x, center_y = w - 70, 70
    radius = 55
    
    overlay = frame.copy()
    cv2.circle(overlay, (center_x, center_y), radius, (10, 20, 10), -1)
    cv2.circle(frame, (center_x, center_y), radius, (0, 255, 0), 1)
    cv2.circle(frame, (center_x, center_y), int(radius * 0.66), (0, 180, 0), 1)
    cv2.circle(frame, (center_x, center_y), int(radius * 0.33), (0, 120, 0), 1)
    
    cv2.line(frame, (center_x - radius, center_y), (center_x + radius, center_y), (0, 100, 0), 1)
    cv2.line(frame, (center_x, center_y - radius), (center_x, center_y + radius), (0, 100, 0), 1)
    cv2.ellipse(frame, (center_x, center_y), (radius, radius), 0, 210, 330, (0, 255, 100), 1)

    radar_angle = (radar_angle + 0.08) % (2 * math.pi)
    sweep_x = int(center_x + radius * math.cos(radar_angle))
    sweep_y = int(center_y + radius * math.sin(radar_angle))
    cv2.line(frame, (center_x, center_y), (sweep_x, sweep_y), (0, 255, 0), 2)
    cv2.circle(frame, (center_x, center_y), 3, (0, 255, 0), -1)

    if primary_user_box is not None:
        p_cx = (primary_user_box[0] + primary_user_box[2]) / 2.0
        
        all_radar_threats = bystanders + gadgets
        for threat in all_radar_threats:
            b_cx = (threat["box"][0] + threat["box"][2]) / 2.0
            dist_norm = max(0.2, min(1.0, 1.0 - (threat["area"] / 80000.0)))
            angle_offset = (b_cx - p_cx) / (w / 2.0) * (math.pi / 3.0)
            blip_x = int(center_x + (dist_norm * (radius - 8)) * math.sin(angle_offset))
            blip_y = int(center_y - (dist_norm * (radius - 8)) * math.cos(angle_offset))
            cv2.circle(frame, (blip_x, blip_y), 4, (0, 0, 255), -1)
            cv2.circle(frame, (blip_x, blip_y), 7, (0, 0, 255), 1)

    cv2.putText(frame, "SPATIAL RADAR", (center_x - 35, center_y + radius + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

# --- MAIN APPLICATION ---
def main():
    global latest_frame, latest_ai_frame, cached_detections, running, full_privacy_override, profile_string, ai_status

    threading.Thread(target=run_api, daemon=True).start()
    ai_engine = EdgeAIEngine()

    root = tk.Tk()
    root.title("EdgeGuard AI Security")
    root.geometry("540x880")
    root.resizable(False, False)
    style = ttk.Style()
    style.theme_use('clam')

    ttk.Label(root, text="Everyday Privacy Controls", font=("Arial", 16, "bold")).pack(pady=8)

    def update_profile():
        global profile_string
        val = profile_var.get()
        if val == 1:
            ai_engine.active_classes = [0, 26, 63, 67, 73]
            profile_string = "Public Cafe Mode"
        elif val == 2:
            ai_engine.active_classes = [0, 73]
            profile_string = "Library/Study Mode"
        elif val == 3:
            ai_engine.active_classes = [0, 63, 67]
            profile_string = "Anti-Snooping Mode"
        status_label.config(text=f"Active Profile: {profile_string}")

    profile_var = tk.IntVar(value=1)
    profile_frame = ttk.LabelFrame(root, text=" 1. Select Environment ", padding=8)
    profile_frame.pack(fill="x", padx=15, pady=4)
    ttk.Radiobutton(profile_frame, text="Public Cafe Mode (Max Bystander Blocking)", variable=profile_var, value=1, command=update_profile).pack(anchor="w")
    ttk.Radiobutton(profile_frame, text="Library/Study Mode (Focus Only)", variable=profile_var, value=2, command=update_profile).pack(anchor="w")
    ttk.Radiobutton(profile_frame, text="Anti-Snooping Mode (Gadget Privacy)", variable=profile_var, value=3, command=update_profile).pack(anchor="w")

    status_label = ttk.Label(root, text="Active Profile: Public Cafe Mode", font=("Arial", 9, "italic"), foreground="green")
    status_label.pack(pady=2)

    sensitivity_frame = ttk.LabelFrame(root, text=" 2. Detection Sensitivity Level ", padding=8)
    sensitivity_frame.pack(fill="x", padx=15, pady=4)
    sensitivity_var = tk.IntVar(value=2)
    ttk.Radiobutton(sensitivity_frame, text="Relaxed (Fewer alerts for busy cafes)", variable=sensitivity_var, value=1).pack(anchor="w")
    ttk.Radiobutton(sensitivity_frame, text="Balanced (Standard protection)", variable=sensitivity_var, value=2).pack(anchor="w")
    ttk.Radiobutton(sensitivity_frame, text="Strict (Immediate trigger for high security)", variable=sensitivity_var, value=3).pack(anchor="w")

    options_frame = ttk.LabelFrame(root, text=" 3. Threat Response Settings ", padding=8)
    options_frame.pack(fill="x", padx=15, pady=4)
    
    collab_mode_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="🫂 Group Collaboration Mode (Whitelists 1 partner)", variable=collab_mode_var).pack(anchor="w", pady=2)
    lock_screen_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="⚠️ Auto-Lock PC", variable=lock_screen_var).pack(anchor="w", pady=2)
    panic_min_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(options_frame, text="🚨 Cafe Panic & Mobile Alerts Enabled", variable=panic_min_var).pack(anchor="w", pady=2)
    snapshot_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(options_frame, text="📸 Save Secure Threat Snapshots Locally", variable=snapshot_var).pack(anchor="w", pady=2)
    silent_mode_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="🔕 Silent Mode (Mutes alarm for Libraries)", variable=silent_mode_var).pack(anchor="w", pady=2)
    inattention_guard_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(options_frame, text="👁️ Opportunistic Exposure Guard (User Inattention Cloak)", variable=inattention_guard_var).pack(anchor="w", pady=2)
    battery_saver_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="🔋 Battery Saver (Manual FPS throttle)", variable=battery_saver_var).pack(anchor="w", pady=2)

    def export_report():
        try:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
            export_path = os.path.join(desktop, f"IT_Security_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
            shutil.copy(audit_log_path, export_path)
            notification.notify(title="Report Exported", message=f"Saved to Desktop", timeout=3)
        except Exception:
            pass
            
    ttk.Button(root, text="📄 Export IT Security Report (CSV)", command=export_report).pack(pady=4)

    def toggle_panic():
        global full_privacy_override
        full_privacy_override = not full_privacy_override
        if full_privacy_override:
            panic_btn.config(text="DISENGAGE DIGITAL WEBCAM COVER", style="PanicActive.TButton")
        else:
            panic_btn.config(text="🛡️ ENGAGE DIGITAL WEBCAM COVER", style="TButton")

    style.configure("PanicActive.TButton", foreground="white", background="red", font=("Arial", 10, "bold"))
    panic_btn = ttk.Button(root, text="🛡️ ENGAGE DIGITAL WEBCAM COVER", command=toggle_panic)
    panic_btn.pack(pady=4, ipadx=8, ipady=2)
    
    def safe_exit():
        global running
        running = False
        root.destroy()
    ttk.Button(root, text="🔒 Close Application & Save Logs", command=safe_exit).pack(side="bottom", pady=5)

    width, height = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    dynamic_threat_score = 0.0
    last_panic_time = 0 
    last_beep_time = 0
    last_toast_time = 0
    prev_time = time.time()
    last_known_person_box = [160, 80, 480, 400] 
    user_distracted_start = 0
    
    # NEW: Temporal variable to prevent flickering zero-trust lockouts
    user_missing_start = 0

    def video_loop_step(cam_context):
        global latest_frame, latest_ai_frame, cached_detections, full_privacy_override, ai_status
        nonlocal prev_time, dynamic_threat_score, last_panic_time, last_beep_time, last_toast_time
        nonlocal last_known_person_box, user_distracted_start, user_missing_start

        if not running: return
            
        loop_delay = 100 if battery_saver_var.get() else 10
        ret_val, video_frame = cap.read()
        
        if not ret_val:
            root.after(loop_delay, lambda: video_loop_step(cam_context))
            return

        s_val = sensitivity_var.get()
        if s_val == 1:
            threat_threshold = 150.0
            inattention_time_limit = 3.5
            threat_step = 1.0
        elif s_val == 3:
            threat_threshold = 50.0
            inattention_time_limit = 1.0
            threat_step = 3.5
        else:
            threat_threshold = 100.0
            inattention_time_limit = 2.0
            threat_step = 2.0

        display_frame = cv2.resize(video_frame, (width, height))
        display_frame = cv2.flip(display_frame, 1)
        
        with frame_lock:
            latest_frame = display_frame.copy()
            latest_ai_frame = enhance_low_light(display_frame).copy()
            local_detections = list(cached_detections)
            current_status = ai_status

        raw_people = [obj for obj in local_detections if obj["class_id"] == 0]
        valid_people = []
        primary_user_box = None
        bystanders = []
        
        if len(raw_people) > 0:
            raw_people.sort(key=lambda x: x["area"], reverse=True)
            primary_user_box = raw_people[0]["box"] 
            valid_people.append(raw_people[0]) 
            
            for i in range(1, len(raw_people)):
                b_box, p_box = raw_people[i]["box"], primary_user_box    
                x_left, y_top = max(p_box[0], b_box[0]), max(p_box[1], b_box[1])
                x_right, y_bottom = min(p_box[2], b_box[2]), min(p_box[3], b_box[3])
                overlap_ratio = (max(0, x_right - x_left) * max(0, y_bottom - y_top)) / raw_people[i]["area"]
                
                if raw_people[i]["area"] > 4000 and overlap_ratio < 0.50:  
                    bystanders.append(raw_people[i])
                    
            if collab_mode_var.get() and len(bystanders) > 0:
                trusted_partner = bystanders.pop(0)
                valid_people.append(trusted_partner)
                tx1, ty1, tx2, ty2 = trusted_partner["box"]
                cv2.rectangle(display_frame, (tx1, ty1), (tx2, ty2), (255, 165, 0), 2)
                cv2.putText(display_frame, "TRUSTED PARTNER", (tx1, max(ty1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)

            valid_people.extend(bystanders)

        # --- 3-SECOND GRACE PERIOD FOR ZERO-TRUST LOCKDOWN ---
        if len(valid_people) == 0:
            if user_missing_start == 0:
                user_missing_start = time.time()
        else:
            user_missing_start = 0

        # Lock if missing for over 3 seconds
        if user_missing_start != 0 and (time.time() - user_missing_start > 3.0) and not full_privacy_override:
            display_frame = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.putText(display_frame, "ZERO-TRUST LOCKDOWN", (120, height // 2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            if int(time.time() * 10) % 50 == 0: 
                log_incident("Critical", "User Absence", "Feed Locked")

            if lock_screen_var.get():
                log_incident("Critical", "User Absence", "OS Workstation Locked for Safety")
                threading.Thread(target=trigger_mobile_alert, args=("LOCKED", "Workstation locked due to user absence."), daemon=True).start()
                ctypes.windll.user32.LockWorkStation()
                time.sleep(2)
        
        else:
            # NORMAL RENDERING LOGIC (Either User is present, OR we are in the 3-second grace period)
            gadgets = [obj for obj in local_detections if obj["class_id"] in [63, 67, 73]]

            for phone in gadgets:
                is_users_phone = False
                if primary_user_box is not None:
                    px1, py1, px2, py2 = primary_user_box
                    bx1, by1, bx2, by2 = phone["box"]
                    x_left, y_top = max(px1, bx1), max(py1, by1)
                    x_right, y_bottom = min(px2, bx2), min(py2, by2)
                    if x_right > x_left and y_bottom > y_top:
                        if ((x_right - x_left) * (y_bottom - y_top) / max(1, phone["area"])) > 0.3: 
                            is_users_phone = True
                
                if not is_users_phone:
                    current_t = time.time()
                    if current_t - last_beep_time > 2.0 and not silent_mode_var.get():
                        winsound.PlaySound("security_alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                        last_beep_time = current_t
                        
                    if panic_min_var.get() and current_t - last_toast_time > 10.0:
                        threading.Thread(target=trigger_mobile_alert, args=("GADGET DETECTED", "Unauthorized background phone/camera detected."), daemon=True).start()
                        if snapshot_var.get():
                            threading.Thread(target=capture_threat_snapshot, args=(display_frame.copy(), "Camera_Detected"), daemon=True).start()
                        last_toast_time = current_t

                    if lock_screen_var.get():
                        ctypes.windll.user32.LockWorkStation()
                        time.sleep(2)
                    break

            local_detections = [obj for obj in local_detections if obj["class_id"] != 0] + valid_people

            if full_privacy_override:
                backup_frame = display_frame.copy()
                small_full = cv2.resize(display_frame, (16, 16), interpolation=cv2.INTER_LINEAR)
                blurred_bg = cv2.resize(small_full, (width, height), interpolation=cv2.INTER_NEAREST)
                
                if primary_user_box is not None:
                    x1, y1, x2, y2 = primary_user_box
                    last_known_person_box = [max(0, x1 - 30), max(0, y1 - 30), min(width, x2 + 30), min(height, y2 + 30)]

                px1, py1, px2, py2 = last_known_person_box
                if (px2 - px1) > 0 and (py2 - py1) > 0:
                    blurred_bg[py1:py2, px1:px2] = backup_frame[py1:py2, px1:px2]

                display_frame = blurred_bg
                cv2.putText(display_frame, "DIGITAL WEBCAM COVER ACTIVE", (20, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            else:
                all_threats = bystanders + gadgets
                for obj in all_threats:
                    x1, y1 = max(0, obj["box"][0]), max(0, obj["box"][1])
                    x2, y2 = min(width, obj["box"][2]), min(height, obj["box"][3])
                    
                    if (x2 - x1) > 0 and (y2 - y1) > 0:
                        roi = display_frame[y1:y2, x1:x2]
                        blurred_roi = cv2.resize(cv2.resize(roi, (16, 16), interpolation=cv2.INTER_LINEAR), (x2 - x1, y2 - y1), interpolation=cv2.INTER_NEAREST)
                        display_frame[y1:y2, x1:x2] = blurred_roi
                        threat_text = "BYSTANDER BLOCKED" if obj["class_id"] == 0 else "GADGET PRIVACY SHIELD"
                        cv2.putText(display_frame, threat_text, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

                if len(bystanders) > 0:
                    max_gaze_multiplier = 0.5
                    for person in bystanders:
                        gaze_mult = calculate_gaze_intent(display_frame, person["box"])
                        if gaze_mult > max_gaze_multiplier: max_gaze_multiplier = gaze_mult
                        
                        if primary_user_box is not None:
                            p_center = (primary_user_box[0] + primary_user_box[2]) / 2
                            b_center = (person["box"][0] + person["box"][2]) / 2
                            direction = "RIGHT" if b_center > p_center else "LEFT"
                            cv2.putText(display_frame, f"THREAT IN {direction} BLIND SPOT", (width // 2 - 120, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    dynamic_threat_score += (threat_step * max_gaze_multiplier)
                    threat_percent = int(min(100, (dynamic_threat_score / threat_threshold) * 100))
                    cv2.rectangle(display_frame, (0, 0), (width, height), (0, 0, int(255 * (threat_percent / 100.0))), 8)
                    cv2.putText(display_frame, f"THREAT MATRIX: {threat_percent}%", (40, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    current_t = time.time()
                    if current_t - last_beep_time > 1.2 and not silent_mode_var.get():
                        winsound.PlaySound("security_alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                        last_beep_time = current_t

                    if current_t - last_toast_time > 8.0:
                        threading.Thread(target=lambda: notification.notify(title="Edge-AI Security Alert", message="Bystander gaze detected.", timeout=3), daemon=True).start()
                        last_toast_time = current_t
                else:
                    dynamic_threat_score = max(0.0, dynamic_threat_score - 4.0)

            if inattention_guard_var.get() and primary_user_box is not None:
                user_gaze = calculate_gaze_intent(display_frame, primary_user_box)
                if user_gaze == 0.5:  
                    if user_distracted_start == 0:
                        user_distracted_start = time.time()
                    elif time.time() - user_distracted_start > inattention_time_limit:
                        cv2.putText(display_frame, "OPPORTUNISTIC RISK: USER LOOKING AWAY", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 2)
                        current_t = time.time()
                        if current_t - last_beep_time > 2.0 and not silent_mode_var.get():
                            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                            last_beep_time = current_t
                else:
                    user_distracted_start = 0

            if dynamic_threat_score >= threat_threshold:
                current_t = time.time()
                if panic_min_var.get() and current_t - last_panic_time > 5.0:
                    threading.Thread(target=trigger_mobile_alert, args=("ESCALATION", "Direct shoulder-surfing gaze detected!"), daemon=True).start()
                    if snapshot_var.get():
                        threading.Thread(target=capture_threat_snapshot, args=(display_frame.copy(), "Direct_Shoulder_Surfer"), daemon=True).start()
                    purge_clipboard()
                    try:
                        active_window = gw.getActiveWindow()
                        if active_window is not None: active_window.minimize()
                    except: pass
                    last_panic_time = current_t
                    dynamic_threat_score = 0.0

            # Draw the radar normally
            draw_spatial_radar(display_frame, primary_user_box, bystanders, gadgets)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        
        cv2.putText(display_frame, f"FPS: {int(fps)}", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(display_frame, current_status, (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255) if "ECO" in current_status else (0, 165, 255), 1)

        cv2.imshow("Local Edge-AI Privacy Guard - Desktop Preview", display_frame)
        if cam_context is not None: cam_context.send(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))

        root.after(loop_delay, lambda: video_loop_step(cam_context))

    threading.Thread(target=bg_inference_worker, args=(ai_engine,), daemon=True).start()

    try:
        with pyvirtualcam.Camera(width=width, height=height, fps=30, fmt=pyvirtualcam.PixelFormat.RGB) as cam:
            root.after(10, lambda: video_loop_step(cam))
            root.mainloop()
    except Exception:
        root.after(10, lambda: video_loop_step(None))
        root.mainloop()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()