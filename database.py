"""commit changes to the database"""
import os
import json
import argparse
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request
import telebot

load_dotenv()
bot = telebot.TeleBot(os.environ["API_KEY"])

def _connect_to_db():
    """function to connect to the database

    Returns:
        connection object: the connection object to the database
    """
    try:
        conn = psycopg2.connect(
            host=os.environ["HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            port=os.environ["PORT"]
        )
        return conn
    except psycopg2.DatabaseError as error:
        print(error)
        return error


def _insert_directory(dirict, table):
    """helper function to insert a dictionary to the table

    Args:
        dirict (dictionary): a dictionary to be inserted in the database
        table (string): a table where the dictionary will be inserted

    Returns:
        string: SQL command to excute it on a connection
    """
    placeholders = ", ".join(["%s"] * len(dirict))
    columns = ", ".join(dirict.keys())
    return f"INSERT INTO {table} ({columns}) VALUES ( {placeholders} )"


def save_job_to_db(username, job, requirements, chat_id):
    """function to save the retrieved job to the database

    Args:
        message (types.Message): information about the sender
    """
    try:
        conn = _connect_to_db()
        cur = conn.cursor()
        sql = _insert_directory(job[username], "jobs")
        cur.execute(sql + "RETURNING job_id", list(job[username].values()))
        lst = cur.fetchone()
        lst_id = lst[0]
        for element in requirements[username]:
            element["job_id"] = lst_id
            sql = _insert_directory(element, "requirements")
            cur.execute(sql, list(element.values()))
        cur.close()
        conn.commit()
    except psycopg2.DatabaseError as error:
        print(error)
    bot.send_message(chat_id,"Okay we got your job description")


def create_tables():
    """function to create tables in the database"""
    try:
        conn = _connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS jobs(\
            job_id SERIAL PRIMARY KEY,\
            job_title VARCHAR(150),\
            job_format VARCHAR(20),\
            job_type varchar(20),\
            job_location VARCHAR(150) NULL,\
            contact VARCHAR(150));"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS requirements(\
            requirement_id SERIAL PRIMARY KEY,\
            requirement_description TEXT,\
            requirement_duration INTEGER DEFAULT 0,\
            job_id INTEGER,\
            CONSTRAINT job_id FOREIGN KEY(job_id) REFERENCES jobs(job_id));"
        )
        cur.close()
        conn.commit()
    except psycopg2.DatabaseError as error:
        print(error)


def fetch_jobs(username, filters, chat_id):
    """function to fetch jobs from the database

    Args:
        username (string): the sender's username
        filters (dictionary): filters for the job

    Returns:
        list: list of jobs that match the client's needs
    """
    elements = [skill["skill_description"] for skill in filters[username]["skills"]]
    try:
        conn = _connect_to_db()
        cur = conn.cursor()

        skills_query = ""
        for skill in elements:
            if len(skills_query) == 0:
                skills_query += "r.requirement_description LIKE '" + skill + "'"
            else:
                skills_query += " OR r.requirement_description LIKE '" + skill + "'"

        sql = f"SELECT j.job_id,j.job_title,j.job_format,j.job_type,j.job_location,j.contact\
                FROM jobs j JOIN(\
                SELECT r.job_id,COUNT(r.job_id) AS matches\
                FROM requirements r WHERE {skills_query}\
                GROUP BY r.job_id) m ON m.job_id=j.job_id\
                WHERE j.job_format='{filters[username]['job_format']}'\
                AND j.job_type='{filters[username]['job_type']}' ORDER BY m.matches DESC;"

        cur.execute(sql)

        jobs = cur.fetchall()
        cur.close()
        for i in jobs:
            job_offer = i[1] + "\n"
            job_offer += i[2]
            if i[2] != "remote":
                job_offer += f" ({i[4]})"
            job_offer += "\n\n"
            job_offer += "About the job\n"
            job_offer += f"Job title: {i[1]}\n"
            job_offer += f"Job type: {i[3]}\n"
            job_offer += f"Job format: {i[2]}"
            if i[2] != "remote":
                job_offer += f" ({i[4]})"
            job_offer += "\n\n"
            job_offer += "Requirements:"
            requirement_list = _fetch_requirements(i[0], chat_id)
            for j in requirement_list:
                job_offer += f"\n- {j[0]} / {j[1]} year"
                if j[1] != 1:
                    job_offer += "s"

            job_offer += f"\n\nContact method: {i[5]}"

            bot.send_message(chat_id, job_offer)
    except psycopg2.DatabaseError as error:
        print(error)


def _fetch_requirements(job_id, _):
    """fetch requirements from the database

    Args:
        job_id (integer): job ID that we need to fetch

    Returns:
        list: requirements list
    """
    try:
        conn = _connect_to_db()
        cur = conn.cursor()

        cur.execute(
            f"SELECT requirement_description, requirement_duration\
                FROM requirements r WHERE r.job_id = {job_id}"
        )

        ret = cur.fetchall()
        cur.close()
        return ret
    except psycopg2.DatabaseError as error:
        print(error)
        return error

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_post_request():
    """function to handle database queries

    Returns:
        response: okay response if everythong went as planned
    """
    data = request.data
    req = json.loads(data.decode())
    req = json.loads(req)
    func_name = req['function_name']
    args = req['args']
    globals()[func_name](*args)
    return 'OK'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port_number", type=str)
    args_cmd = parser.parse_args()
    server_port = args_cmd.port_number
    server_port = int(server_port)
    app.run(debug=True, port=server_port)
