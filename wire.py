"""sends data to the middle server"""
import json
import os
from dotenv import load_dotenv

load_dotenv()
WIRE_URL = os.environ["WIRE_URL"]


def send_data(_):
    # send payload to the second server
    pass


def save_job_to_db(username, job, requirements, chat_id):
    payload = {
        "function_name": "save_job_to_db",
        "args": [username, job, requirements, chat_id],
        "chat_id": chat_id,
    }
    send_data(json.dumps(payload))


def create_tables():
    payload = {"function_name": "create_tables", "args": []}
    send_data(json.dumps(payload))


def fetch_jobs(username, filters, chat_id):
    payload = {
        "function_name": "fetch_jobs",
        "args": [username, filters, chat_id],
        "chat_id": chat_id,
    }
    send_data(json.dumps(payload))


def fetch_requirements(job_id, chat_id):
    payload = {"function_name": "job_id", "args": [job_id, chat_id], "chat_id": chat_id}
    send_data(json.dumps(payload))
