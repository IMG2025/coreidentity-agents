import os
import paramiko
import logging
from datetime import datetime, timedelta
import requests

from dotenv import load_dotenv
load_dotenv()

# ✅ CONFIGURATION
SFTP_HOST = "s-9b0f88558b264dfda.server.transfer.us-east-1.amazonaws.com"
SFTP_USERNAME = os.getenv("TOAST_SFTP_USERNAME")
KEY_PATH = os.getenv("TOAST_SSH_KEY_PATH")
LOCAL_SAVE_DIR = "./toast_exports"
GUIDS = ["57130", "57138"]  # Toast GUIDs

# ✅ LOGGING
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ TELEGRAM
def notify_telegram(message):
    try:
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7951699971:AAGIzYMzE8fgmlaRJ05CqkODFbegKw6z0sA")
        TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8102731631")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        logging.warning(f"Telegram notification failed: {e}")

def fetch_exports():
    dates_to_try = [
        datetime.now().strftime("%Y%m%d"),
        (datetime.now() - timedelta(days=1)).strftime("%Y%m%d"),
    ]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        logging.info(f"Connecting to {SFTP_HOST} as {SFTP_USERNAME}")
        key = paramiko.RSAKey.from_private_key_file(KEY_PATH)
        client.connect(SFTP_HOST, username=SFTP_USERNAME, pkey=key)

        sftp = client.open_sftp()
        success = False

        for guid in GUIDS:
            for export_date in dates_to_try:
                remote_path = f"/{guid}/{export_date}/"
                try:
                    sftp.chdir(remote_path)
                    logging.info(f"✅ Found directory: {remote_path}")

                    local_path_dir = os.path.join(LOCAL_SAVE_DIR, guid, export_date)
                    os.makedirs(local_path_dir, exist_ok=True)

                    files = sftp.listdir()
                    logging.info(f"📦 {len(files)} files found in {remote_path}")

                    for filename in files:
                        local_file = os.path.join(local_path_dir, filename)
                        sftp.get(filename, local_file)
                        logging.info(f"⬇️  Downloaded: {filename} → {local_file}")
                        notify_telegram(f"✅ SignalFetch: `{filename}` downloaded for GUID {guid} ({export_date})")

                    success = True
                    break  # Skip to next GUID once found

                except FileNotFoundError:
                    logging.warning(f"❌ No export directory found for: {remote_path}")

        sftp.close()
        if not success:
            logging.info("No exports found for any date.")
        else:
            logging.info("✅ Toast export sync complete.")

    except Exception as e:
        logging.error(f"❌ SignalFetch SSH Error: {e}")

    finally:
        client.close()

if __name__ == "__main__":
    fetch_exports()
