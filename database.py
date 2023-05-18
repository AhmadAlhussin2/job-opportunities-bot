"""commit changes to the database"""
import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()
HOST = os.environ["HOST"]
USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]


def connect_to_db():
    """function to connect to the database

    Returns:
        connection object: the connection object to the database
    """
    try:
        conn = psycopg2.connect(
            host=HOST, database="telegram-bot", user=USER, password=DB_PASSWORD
        )
        return conn
    except psycopg2.DatabaseError as error:
        print(error)
        return error


def insert_directory(dirict, table):
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


def save_job_to_db(username, job, requirements, _):
    """function to save the retrieved job to the database

    Args:
        message (types.Message): information about the sender
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        sql = insert_directory(job[username], "jobs")
        cur.execute(sql + "RETURNING job_id", list(job[username].values()))
        lst = cur.fetchone()
        lst_id = lst[0]
        for element in requirements[username]:
            element["job_id"] = lst_id
            sql = insert_directory(element, "requirements")
            cur.execute(sql, list(element.values()))
        cur.close()
        conn.commit()
    except psycopg2.DatabaseError as error:
        print(error)


def create_tables():
    """function to create tables in the database"""
    try:
        conn = connect_to_db()
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


def fetch_jobs(username, filters, _):
    """function to fetch jobs from the database

    Args:
        username (string): the sender's username
        filters (dictionary): filters for the job

    Returns:
        list: list of jobs that match the client's needs
    """
    skills = filters[username]["skills"]
    elements = [skill["skill_description"] for skill in skills]
    try:
        conn = connect_to_db()
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

        ret = cur.fetchall()
        cur.close()
        return ret
    except psycopg2.DatabaseError as error:
        print(error)
        return error


def fetch_requirements(job_id, _):
    """fetch requirements from the database

    Args:
        job_id (integer): job ID that we need to fetch

    Returns:
        list: requirements list
    """
    try:
        conn = connect_to_db()
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
