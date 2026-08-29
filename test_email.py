import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "yaswanthsai5704@gmail.com"
SENDER_PASSWORD = "jtdrvrtrzylbrnvl"  # No spaces
RECIPIENT_EMAIL = "yaswanthsai5704@gmail.com"

try:
    print("[1/3] Connecting to Gmail SMTP Server...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
    server.starttls()
    
    print("[2/3] Authenticating credentials...")
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    
    print("[3/3] Sending test security alert...")
    msg = MIMEText("EdgeGuard Diagnostic Test: SMTP Connection Successful.", "plain")
    msg["Subject"] = "🚨 EdgeGuard Diagnostic Test"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    server.quit()
    print("\n✅ SUCCESS: Email sent successfully! Check your inbox/spam.")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")