import json
import re   

from urllib3 import request
import functions_framework
from google.cloud import storage, pubsub_v1

PROJECT = "project-f131ec20-0df6-4cfa-bf0"
BUCKET = "cs528-12kfiles-bucket-thomas"
PREFIX = "12k-files/"
   
def norm(s):
    return s.strip().lower().replace("_", " ").replace("-", " ")

FORBIDDEN = {norm(c) for c in
    ["North Korea", "Iran", "Cuba", "Myanmar", "Iraq",
    "Libya", "Sudan", "Zimbabwe", "Syria"]}

bucket = storage.Client().bucket(BUCKET)
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT, "forbidden-requests")

def log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}))

@functions_framework.http
def handle(request):
    if request.method not in ("GET", "POST"):
        log("WARNING", "501 not implemented", method=request.method)
        print("501 not implemented:", request.method, request.path)
        return "Not implemented", 501

    country = request.headers.get("X-country", "")
    print("X-country seen:", repr(country))
    if norm(country) in FORBIDDEN:
        log("ERROR", "forbidden country", country=country, path=request.path)
        print("400 forbidden country:", country, request.path)
        publisher.publish(topic_path, json.dumps(
            {"country": country, "path": request.path}).encode()).result()
        return "Permission denied", 400
    
    if request.method == "GET":
        name = request.path.lstrip("/")
    else:
        name = (request.get_json(silent=True) or {}).get("file") or request.form.get("file", "")

    name = name.removeprefix("12k-files/")
    m = re.fullmatch(r"(\d+)\.html", name)
    if m:
        name = f"file_{m.group(1)}.txt"

    blob = bucket.blob(PREFIX + name)
    if not name or not blob.exists():
        log("ERROR", "404 file not found", file=name)
        return "File not found", 404
    return blob.download_as_text(), 200