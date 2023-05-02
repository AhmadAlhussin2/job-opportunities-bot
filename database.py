import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()
HOST = os.environ["HOST"]
USER = os.environ["USER"]
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


def insert_directory(dir, table):
    """helper function to insert a dictionary to the table

    Args:
        dir (dictionary): a dictionary to be inserted in the database
        table (string): a table where the dictionary will be inserted

    Returns:
        string: SQL command to excute it on a connection
    """
    placeholders = ", ".join(["%s"] * len(dir))
    columns = ", ".join(dir.keys())
    return "INSERT INTO %s (%s) VALUES ( %s )" % (table, columns, placeholders)


def save_job_to_db(message,job,requirements):
    """function to save the retrieved job to the database

    Args:
        message (types.Message): information about the sender
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        sql = insert_directory(job[message.from_user.username], "jobs")
        cur.execute(
            sql + "RETURNING job_id", list(job[message.from_user.username].values())
        )
        lst = cur.fetchone()
        lst_id = lst[0]
        for element in requirements[message.from_user.username]:
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
            job_location VARCHAR(150) NULL);"
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
        
def fetch_jobs(message,filters):
    skills = filters[message.from_user.username]['skills']
    elements = [skill['skill_description'] for skill in skills]
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        skills_query = ""
        for skill in elements:
            if len(skills_query) == 0:
                skills_query += "r.requirement_description LIKE '"+skill+"'"
            else:
                skills_query += " OR r.requirement_description LIKE '"+skill+"'"
        
        sql = "SELECT j.job_id,j.job_title,j.job_format,j.job_type,j.job_location FROM jobs j JOIN(\
                SELECT r.job_id,COUNT(r.job_id) AS matches\
                FROM requirements r WHERE %s\
                GROUP BY r.job_id) m ON m.job_id=j.job_id ORDER BY m.matches DESC;" % skills_query
    
        cur.execute(sql)
        
        ret = cur.fetchall()
        cur.close()
        return ret
    except psycopg2.DatabaseError as error:
        print(error)
        
def fetch_requirements(job_id):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        sql = f"SELECT requirement_description, requirement_duration FROM requirements r WHERE r.job_id = {job_id}"
    
        cur.execute(sql)
        
        ret = cur.fetchall()
        cur.close()
        return ret
    except psycopg2.DatabaseError as error:
        print(error)