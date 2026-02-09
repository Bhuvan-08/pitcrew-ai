from flask import Flask
import os
import time

app = Flask(__name__)

BROKEN = False

@app.route("/")
def home():
    return "PitCrew Demo App Running"

@app.route("/health")
def health():
    if os.path.exists("broken.flag"):
        time.sleep(3)
        return "SERVICE UNHEALTHY", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
