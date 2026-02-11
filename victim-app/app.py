from flask import Flask, jsonify
import os
import time
import logging
import sys

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

SERVICE_NAME = "payment-gateway"


@app.route("/")
def home():
    return "PitCrew Demo App Running"


@app.route("/health")
def health():
    """
    Health endpoint used by the Observability (Mechanic) agent.
    Returns rich telemetry, not just up/down.
    """

    # -------- Failure Mode --------
    if os.path.exists("broken.flag"):
        logging.critical(
        "[CRITICAL] MemoryAllocationFailure | service=payment-gateway | container=prod-api | memory=98.7%% | action=restart"
        )


        # Simulate latency under stress
        time.sleep(3)

        return jsonify({
            "service": SERVICE_NAME,
            "status": "CRITICAL",
            "cpu_load": 98.7,
            "memory_usage_mb": 1024,
            "active_threads": 487,
            "recommendation": "RESTART_SERVICE"
        }), 500

    logging.info(
        "[INFO] Service '%s' operating within normal parameters.",
        SERVICE_NAME
    )

    return jsonify({
        "service": SERVICE_NAME,
        "status": "OK",
        "cpu_load": 23.4,
        "memory_usage_mb": 312,
        "active_threads": 14
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
