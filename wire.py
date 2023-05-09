"""sends data to the middle server"""
import json
import os
from dotenv import load_dotenv

load_dotenv()
WIRE_URL = os.environ["WIRE_URL"]


def send_data(_):
    """Funciton to send data to the middle server

    Args:
        _ (string): payload to be sent
    """
    # send payload to the second server
    return


def save_job_to_db(username, job, requirements, chat_id):
    """function to send command for saving a job in the database

    Args:
        username (string): the sender's username
        job (dictionary): the job description
        requirements (dictionary): the requiremnets description
        chat_id (integer): the chat ID of the sender
    """
    payload = {
        "function_name": "save_job_to_db",
        "args": [username, job, requirements, chat_id],
        "chat_id": chat_id,
    }
    send_data(json.dumps(payload))


def create_tables():
    """function to send a command to the middle server for createing tables"""
    payload = {"function_name": "create_tables", "args": []}
    send_data(json.dumps(payload))


def fetch_jobs(username, filters, chat_id):
    """function to send a command for fetching jobs

    Args:
        username (string): the username of the sender
        filters (dictionary): the skils that the candidate has
        chat_id (integer): the chat ID of the sender
    """
    payload = {
        "function_name": "fetch_jobs",
        "args": [username, filters, chat_id],
        "chat_id": chat_id,
    }
    send_data(json.dumps(payload))


def fetch_requirements(job_id, chat_id):
    """function to fetch the requirements of a specific job

    Args:
        job_id (integer): a unique identifier for the job
        chat_id (integer): the chat ID of the sender
    """
    payload = {"function_name": "job_id", "args": [job_id, chat_id], "chat_id": chat_id}
    send_data(json.dumps(payload))
