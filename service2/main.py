import json
import datetime
import subprocess
from google.oauth2.credentials import Credentials
from google.cloud import pubsub_v1, storage

PROJECT = "project-f131ec20-0df6-4cfa-bf0"
BUCKET = "cs528-12kfiles-bucket-thomas"
SA = f"hw3-sa@{PROJECT}.iam.gserviceaccount.com"
LOG_OBJECT = "forbidden-logs/forbidden.txt"

def fetch_token(request, scopes):
    tok = subprocess.run(
        ["gcloud", "auth", "print-access-token", f"--impersonate-service-account={SA}"],
        capture_output=True, text=True, check=True).stdout.strip()
    expiry = (datetime.datetime.now(datetime.timezone.utc)
              + datetime.timedelta(minutes=50)).replace(tzinfo=None)
    return tok, expiry

creds = Credentials(token=None, refresh_handler=fetch_token)

subscriber = pubsub_v1.SubscriberClient(credentials=creds)
bucket = storage.Client(credentials=creds, project=PROJECT).bucket(BUCKET)

def callback(msg):
    info = json.loads(msg.data)
    line = f"FORBIDDEN request from {info['country']} for {info['path']}\n"
    print(line, end="", flush=True)
    blob = bucket.blob(LOG_OBJECT)
    old = blob.download_as_text() if blob.exists() else ""
    blob.upload_from_string(old + line)   # GCS can't append, so rewrite the object
    msg.ack()

path = subscriber.subscription_path(PROJECT, "forbidden-sub")
print("Listening on", path, flush=True)
subscriber.subscribe(path, callback=callback).result()