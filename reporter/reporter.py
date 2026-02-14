import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)


def generate_postmortem(
    incident_id,
    service,
    root_cause,
    resolution,
    detection_time,
    recovery_time
):

    duration = (recovery_time - detection_time).total_seconds()

    filename = f"POST_MORTEM_INC_{incident_id}.md"
    filepath = os.path.join(REPORTS_DIR, filename)

    content = f"""
# Incident Report

Incident ID: {incident_id}
Service: {service}

Root Cause:
{root_cause}

Resolution:
{resolution}

Detection Time: {detection_time}
Recovery Time: {recovery_time}

Total Downtime (seconds): {duration}
"""

    with open(filepath, "w") as f:
        f.write(content.strip())

    return filepath, duration
