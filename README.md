# 🛡️ EdgeGuard AI: Local Laptop Privacy Shield



Tired of feeling like someone is reading your screen at the coffee shop? Worried about leaving your laptop unattended? 

EdgeGuard is an intelligent, locally hosted Edge-AI privacy shield. Using advanced computer vision, it monitors your background and instantly neutralizes visual hacking threats before they can steal your data.

---

## 🚀 Quick Download
**[Download the ready-to-use Windows .exe App directly](https://github.com/YASWANTH1976/edgeguard/releases/latest/download/edgeguard.zip)**

---

## 🔥 Key Features

*   🎯 **Intent-Aware Threat Matrix:** Calculates 3D head yaw using Google MediaPipe. It ignores bystanders just walking past, but triggers an escalation if someone actively stares at your screen.
*   📡 **3D Spatial Radar & Blind-Spot Warning:** Transforms 2D video into a top-down tactical radar. Alerts you if a physical threat is loitering specifically in your left or right blind spot.
*   📱 **Smart Gadget Suppression:** If a bystander holds up a phone camera, EdgeGuard isolates the device using Intersection over Union (IoU), blocks it with a targeted pixel mask, and sounds a custom security siren.
*   🫂 **Group Collaboration Mode:** Working with a friend? Whitelist the person sitting closest to you as a "Trusted Partner" so you can work together without triggering the alarm.
*   🚨 **Cafe Panic Mode & Auto-Lock:** If a critical threat is detected, EdgeGuard intercepts your OS to instantly minimize all open windows (Win + D), purges your clipboard RAM, and locks your workstation if you step away.
*   📸 **Privacy-Preserving Audit Trail:** Automatically captures a timestamped snapshot of an attack. The attacker's face is blurred *before* saving to comply with GDPR/privacy laws, and logs are hashed using SHA-256 cryptography.
*   🔋 **100% Offline Eco-Standby:** Powered by an ONNX-compiled Edge AI engine. Uses frame-delta thresholding to pause heavy processing when you are still, preventing thermal throttling and saving laptop battery.

## 💻 Developer Quick Start (Python)

If you want to run the raw code or contribute to the project:

**1. Clone the repository:**
```bash
git clone [https://github.com/YASWANTH1976/edgeguard.git](https://github.com/YASWANTH1976/edgeguard.git)
cd edgeguard
2. Install the required dependencies:

Bash
pip install ultralytics mediapipe opencv-python pyvirtualcam flask plyer pygetwindow pystray
3. Configure Mobile Push Alerts:
Open main.py and navigate to Line 78. Insert your 16-digit Google App Password to enable emergency SMTP push notifications to your phone:

Python
SENDER_PASSWORD = "your-16-digit-app-password"
4. Run the Application:

Bash
python main.py
