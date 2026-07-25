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

# --- OS INTEGRATION IMPORTS ---
import winsound
import ctypes
from plyer import notification

"""
================================================================================
              EVERYDAY CONSUMER PRIVACY GUARD (PRODUCTION BUILD)
================================================================================
PHASE 1-4: ONNX Compilation, Multithreading, Sub-Sampling, Loopback.
PHASE 5-7: Eco-Standby, Auto-Lock, OS Toast Notifications, Geometric Anti-Ghosting.
PHASE 8-9: Panic Minimize (Win+D) & Enterprise Clipboard RAM Purging.
PHASE 10: Consumer Accessibility (Silent Library Mode & Battery Saver Throttling).
================================================================================
"""

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
            print("[INFO] ONNX model not found. Exporting PyTorch to ONNX Graph...")
            model = YOLO(self.pt_path)
            model.export(format="onnx", imgsz=self.img_size[0])
        self.model = YOLO(self.onnx_path, task="detect")

    def process_frame(self, frame):
        results = self.model(frame, conf=0.40, verbose=False, imgsz=640)
        detected_objects = []
        if results and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                if cls_id in self.active_classes:
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    label = self.model.names[cls_id]
                    area = (xyxy[2] - xyxy[0]) * (xyxy[3] - xyxy[1])
                    detected_objects.append({
                        "box": xyxy, "label": label, "class_id": cls_id, "area": area
                    })
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

last_beep_time = 0
last_toast_time = 0
last_panic_time = 0 

audit_log_path = f"compliance_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
with open(audit_log_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Threat Level", "Object Redacted", "Action Taken"])

def log_incident(threat_level, object_label, action="Sub-Sampling Redaction"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(audit_log_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, threat_level, object_label, action])

def enhance_low_light(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    if mean_brightness < 80:
        gamma = 1.5
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(frame, table)
    return frame

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
                motion_level = np.sum(thresh)
                if motion_level < 50000: 
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

def main():
    global latest_frame, latest_ai_frame, cached_detections, running, full_privacy_override, profile_string, ai_status
    global last_beep_time, last_toast_time, last_panic_time
    
    ai_engine = EdgeAIEngine()

    root = tk.Tk()
    root.title("Personal Privacy Guard")
    root.geometry("500x520")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use('clam')

    title_label = ttk.Label(root, text="Everyday Privacy Controls", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)

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
    profile_frame = ttk.LabelFrame(root, text=" 1. Select Environment ", padding=10)
    profile_frame.pack(fill="x", padx=20, pady=5)

    ttk.Radiobutton(profile_frame, text="Public Cafe Mode (Max Bystander Blocking)", variable=profile_var, value=1, command=update_profile).pack(anchor="w")
    ttk.Radiobutton(profile_frame, text="Library/Study Mode (Focus Only)", variable=profile_var, value=2, command=update_profile).pack(anchor="w")
    ttk.Radiobutton(profile_frame, text="Anti-Snooping Mode (Gadget Privacy)", variable=profile_var, value=3, command=update_profile).pack(anchor="w")

    status_label = ttk.Label(root, text="Active Profile: Public Cafe Mode", font=("Arial", 10, "italic"), foreground="green")
    status_label.pack(pady=5)

    options_frame = ttk.LabelFrame(root, text=" 2. Threat Response Settings ", padding=10)
    options_frame.pack(fill="x", padx=20, pady=5)

    lock_screen_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="⚠️ Auto-Lock PC (When I step away or threat detected)", variable=lock_screen_var).pack(anchor="w", pady=2)

    panic_min_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="🚨 Cafe Panic (Minimizes screen & clears clipboard on threat)", variable=panic_min_var).pack(anchor="w", pady=2)
    
    silent_mode_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="🔕 Silent Mode (Mutes alarm for Libraries)", variable=silent_mode_var).pack(anchor="w", pady=2)
    
    battery_saver_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(options_frame, text="🔋 Battery Saver (Lowers processing speed to save power)", variable=battery_saver_var).pack(anchor="w", pady=2)

    def toggle_panic():
        global full_privacy_override
        full_privacy_override = not full_privacy_override
        if full_privacy_override:
            panic_btn.config(text="DISENGAGE DIGITAL WEBCAM COVER", style="PanicActive.TButton")
        else:
            panic_btn.config(text="🛡️ ENGAGE DIGITAL WEBCAM COVER", style="TButton")

    style.configure("PanicActive.TButton", foreground="white", background="red", font=("Arial", 11, "bold"))
    panic_btn = ttk.Button(root, text="🛡️ ENGAGE DIGITAL WEBCAM COVER", command=toggle_panic)
    panic_btn.pack(pady=10, ipadx=10, ipady=5)

    def safe_exit():
        global running
        running = False
        root.destroy()

    exit_btn = ttk.Button(root, text="🔒 Close Application & Save Logs", command=safe_exit)
    exit_btn.pack(side="bottom", pady=10)

    width, height = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    fps_records = []
    total_objects_masked = 0
    prev_time = time.time()
    alert_toggle = False 
    last_known_person_box = [160, 80, 480, 400] 

    def video_loop_step(cam_context):
        global latest_frame, latest_ai_frame, cached_detections, full_privacy_override, ai_status
        global last_beep_time, last_toast_time, last_panic_time
        nonlocal prev_time, total_objects_masked, last_known_person_box, alert_toggle

        if not running:
            return
            
        loop_delay = 100 if battery_saver_var.get() else 10

        ret_val, video_frame = cap.read()
        if not ret_val:
            root.after(loop_delay, lambda: video_loop_step(cam_context))
            return

        display_frame = cv2.resize(video_frame, (width, height))
        display_frame = cv2.flip(display_frame, 1)
        ai_ready_frame = enhance_low_light(display_frame)

        with frame_lock:
            latest_frame = display_frame.copy()
            latest_ai_frame = ai_ready_frame.copy()
            local_detections = list(cached_detections)
            current_status = ai_status

        raw_people = [obj for obj in local_detections if obj["class_id"] == 0]
        valid_people = []
        primary_user_box = None
        shoulder_surfing_active = False
        
        if len(raw_people) > 0:
            raw_people.sort(key=lambda x: x["area"], reverse=True)
            primary_user_box = raw_people[0]["box"] 
            valid_people.append(raw_people[0]) 
            
            for i in range(1, len(raw_people)):
                b_box = raw_people[i]["box"] 
                p_box = primary_user_box     
                
                x_left = max(p_box[0], b_box[0])
                y_top = max(p_box[1], b_box[1])
                x_right = min(p_box[2], b_box[2])
                y_bottom = min(p_box[3], b_box[3])
                
                intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)
                overlap_ratio = intersection_area / raw_people[i]["area"]
                
                # FIXED THRESHOLD: Lowered to 4000 to catch people further in the background
                if raw_people[i]["area"] > 4000 and overlap_ratio < 0.50:  
                    valid_people.append(raw_people[i])
                    
            if len(valid_people) > 1:
                shoulder_surfing_active = True

        cleaned_detections = [obj for obj in local_detections if obj["class_id"] != 0] + valid_people
        local_detections = cleaned_detections
        people = valid_people

        if len(people) == 0 and not full_privacy_override:
            display_frame = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.putText(display_frame, "ZERO-TRUST LOCKDOWN", (120, height // 2 - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.putText(display_frame, "USER ABSENT. BACKGROUND ISOLATED.", (80, height // 2 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            if int(time.time() * 10) % 50 == 0: 
                log_incident("Critical", "User Absence", "Feed Locked")

            if lock_screen_var.get():
                log_incident("Critical", "User Absence", "OS Workstation Locked for Safety")
                ctypes.windll.user32.LockWorkStation()
                time.sleep(2)
                
        else:
            if full_privacy_override:
                backup_frame = display_frame.copy()
                small_full = cv2.resize(display_frame, (16, 16), interpolation=cv2.INTER_LINEAR)
                blurred_background = cv2.resize(small_full, (width, height), interpolation=cv2.INTER_NEAREST)
                
                if primary_user_box is not None:
                    x1, y1, x2, y2 = primary_user_box
                    last_known_person_box = [max(0, x1 - 30), max(0, y1 - 30), min(width, x2 + 30), min(height, y2 + 30)]

                px1, py1, px2, py2 = last_known_person_box
                if (px2 - px1) > 0 and (py2 - py1) > 0:
                    blurred_background[py1:py2, px1:px2] = backup_frame[py1:py2, px1:px2]

                display_frame = blurred_background
                cv2.putText(display_frame, "DIGITAL WEBCAM COVER ACTIVE", (20, height - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            for obj in local_detections:
                is_primary_user = (obj["class_id"] == 0 and primary_user_box is not None and np.array_equal(obj["box"], primary_user_box))
                if is_primary_user:
                    continue  
                
                x1, y1, x2, y2 = obj["box"]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                if (x2 - x1) > 0 and (y2 - y1) > 0:
                    roi = display_frame[y1:y2, x1:x2]
                    small_roi = cv2.resize(roi, (16, 16), interpolation=cv2.INTER_LINEAR)
                    blurred_roi = cv2.resize(small_roi, (x2 - x1, y2 - y1), interpolation=cv2.INTER_NEAREST)
                    display_frame[y1:y2, x1:x2] = blurred_roi
                    
                    threat_text = "BYSTANDER BLOCKED" if obj["class_id"] == 0 else "PRIVACY SHIELD ACTIVE"
                    cv2.putText(display_frame, threat_text, (x1, max(y1 - 10, 20)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                    
                    if int(time.time() * 10) % 20 == 0: 
                        log_incident("High" if obj["class_id"] == 0 else "Medium", obj["label"], "Pixelation Applied")
                        total_objects_masked += 1

            if shoulder_surfing_active:
                alert_toggle = not alert_toggle
                color = (0, 0, 255) if alert_toggle else (0, 100, 255)
                cv2.rectangle(display_frame, (0, 0), (width, height), color, 8)
                cv2.putText(display_frame, "WARNING: BYSTANDER DETECTED", (40, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                current_t = time.time()

                if current_t - last_beep_time > 2.0 and not silent_mode_var.get():
                    threading.Thread(target=lambda: winsound.Beep(1000, 400), daemon=True).start()
                    last_beep_time = current_t

                if current_t - last_toast_time > 8.0:
                    def send_toast():
                        notification.notify(
                            title="Edge-AI Security Alert",
                            message="Unauthorized bystander detected behind you. Securing data.",
                            app_icon=None,
                            timeout=3
                        )
                    threading.Thread(target=send_toast, daemon=True).start()
                    last_toast_time = current_t
                
                if panic_min_var.get() and current_t - last_panic_time > 5.0:
                    log_incident("Critical", "Bystander", "Panic Minimize & Clipboard Purged")
                    purge_clipboard()
                    ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0) 
                    ctypes.windll.user32.keybd_event(0x44, 0, 0, 0) 
                    ctypes.windll.user32.keybd_event(0x44, 0, 2, 0) 
                    ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0) 
                    last_panic_time = current_t

                if lock_screen_var.get():
                    log_incident("Critical", "Bystander", "OS Workstation Locked")
                    ctypes.windll.user32.LockWorkStation()
                    time.sleep(2) 

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        if 0 < fps < 100:
            fps_records.append(fps)
        
        cv2.putText(display_frame, f"FPS: {int(fps)}", (20, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        ai_color = (0, 255, 255) if "ECO" in current_status else (0, 165, 255)
        cv2.putText(display_frame, current_status, (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ai_color, 1)
        
        if battery_saver_var.get():
            cv2.putText(display_frame, "BATTERY SAVER ON", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Local Edge-AI Privacy Guard - Desktop Preview", display_frame)
        
        if cam_context is not None:
            ecc_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            cam_context.send(ecc_frame)

        root.after(loop_delay, lambda: video_loop_step(cam_context))

    ai_thread = threading.Thread(target=bg_inference_worker, args=(ai_engine,), daemon=True)
    ai_thread.start()

    try:
        with pyvirtualcam.Camera(width=width, height=height, fps=30, fmt=pyvirtualcam.PixelFormat.RGB) as cam:
            root.after(10, lambda: video_loop_step(cam))
            root.mainloop()
    except Exception as e:
        print(f"\n[WARNING] Virtual Camera not detected. Running local desktop preview mode.\nDetails: {e}")
        root.after(10, lambda: video_loop_step(None))
        root.mainloop()

    cap.release()
    cv2.destroyAllWindows()

    if len(fps_records) > 0:
        avg_fps = int(np.mean(fps_records))
        log_content = (
            f"=========================================\n"
            f"     CAPSTONE PERFORMANCE METRIC LOG     \n"
            f"=========================================\n"
            f"Target AI Framework Model : YOLO26-Nano (ONNX Compiled)\n"
            f"Hardware Platform Config  : Host Intel CPU (Local Engine)\n"
            f"User Profile Selected     : {profile_string}\n"
            f"Calculated Average Speed  : {avg_fps} FPS\n"
            f"Total Objects Obfuscated  : {total_objects_masked} occurrences\n"
            f"Status Evaluation         : PRODUCTION CONSUMER BUILD\n"
            f"=========================================\n"
        )
        with open("performance_log.txt", "w", encoding="utf-8") as f:
            f.write(log_content)
        print("\n[SUCCESS] Session data closed safely.")
        print("[SUCCESS] Performance metrics exported to 'performance_log.txt'")
        print(f"[SUCCESS] Compliance data exported to '{audit_log_path}'")

if __name__ == "__main__":
    main()