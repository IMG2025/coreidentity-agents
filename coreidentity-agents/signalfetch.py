import os
import paramiko
import logging
import base64
import requests
from datetime import datetime, timedelta

# ✅ ENV VARS
SFTP_HOST = os.getenv("TOAST_SFTP_HOST")
SFTP_USERNAME = os.getenv("TOAST_SFTP_USERNAME")
PRIVATE_KEY_B64 = os.getenv("TOAST_SFTP_PRIVATE_KEY")  # Corrected to match Render.yaml
LOCAL_SAVE_DIR = "./coreidentity-agents/toast_exports"
GUIDS = ["57130", "57138"]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_export_dates():
    today = datetime.now().strftime("%Y%m%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    return [today, yesterday]

def notify_telegram(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        except Exception as e:
            logging.warning(f"Telegram notification failed: {e}")

def fetch_toast_exports():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if not PRIVATE_KEY_B64:
            raise Exception("❌ Missing TOAST_SFTP_PRIVATE_KEY")

        private_key_bytes = base64.b64decode(PRIVATE_KEY_B64)
        temp_key_path = "/tmp/temp_key.pem"
        with open(temp_key_path, "wb") as f:
            f.write(private_key_bytes)

        private_key = paramiko.RSAKey.from_private_key_file(temp_key_path)
        logging.info(f"Connecting to {SFTP_HOST} as {SFTP_USERNAME}")
        client.connect(SFTP_HOST, username=SFTP_USERNAME, pkey=private_key)
        sftp = client.open_sftp()

        for guid in GUIDS:
            for date in get_export_dates():
                remote_path = f"/{guid}/{date}/"
                try:
                    sftp.chdir(remote_path)
                    logging.info(f"✅ Found directory: {remote_path}")
                    local_path = os.path.join(LOCAL_SAVE_DIR, guid, date)
                    os.makedirs(local_path, exist_ok=True)

                    for filename in sftp.listdir():
                        remote_file = f"{remote_path}{filename}"
                        local_file = os.path.join(local_path, filename)
                        sftp.get(filename, local_file)
                        logging.info(f"⬇️  Downloaded: {filename} → {local_file}")
                        notify_telegram(f"📦 SignalFetch: `{filename}` for {guid} ({date})")
                    break
                except FileNotFoundError:
                    logging.warning(f"❌ No export directory found for: {remote_path}")

        sftp.close()
        logging.info("✅ Toast export sync complete.")
    except Exception as e:
        logging.error(f"❌ SignalFetch SSH Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fetch_toast_exports()
