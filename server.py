import telebot
import os
import psycopg2
from dotenv import load_dotenv
from markups import job_type_markup,job_format_markup, stop_requirments_markup
from constants import *
from telebot import types


load_dotenv()
API_KEY = os.environ["API_KEY"]
HOST = os.environ["HOST"]
USER = os.environ["USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

bot = telebot.TeleBot(API_KEY)
global job,requirements
job = {}
requirements = {}

@bot.message_handler(commands=["post_job"])
def post_job(message):
    """post job function to handle recieveing job details and adding them to the databse

    Args:
        message (types.Message): a command to initite the process (post_job for now)
    """
    bot.send_message(
        message.chat.id,
        "Thanks for using job opportunities bot\nTo post a new job please answer the following questions:",
    )
    job[message.from_user.username] = {}
    msg = bot.send_message(message.chat.id, "What is the job title?")
    bot.register_next_step_handler(msg, wait_for_job_name)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """function to handle all the callbacks from custom keyboards

    Args:
        call (types.CallbackQuery): the callback data to be handled
    """
    if call.data in (job.lower() for job in JOB_TYPES):
        register_job_type(call.message, call)
    elif call.data in JOB_FORMATS:
        register_job_format(call.message, call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


def wait_for_job_name(message):
    """function to retrieve the job name from the user

    Args:
        message (types.Message): job name with inforamtion about user
    """
    chat_id = message.chat.id
    name = message.text
    bot.send_message(chat_id, f"Okay you chose '{name}' to be you job's name")
    job[message.from_user.username]["job_title"] = name
    bot.send_message(
        chat_id, "What is the type of your job?", reply_markup=job_type_markup()
    )


def wait_for_job_location(message):
    """function to retrive the job location

    Args:
        message (types.Message): job location with inforamtion about user
    """
    chat_id = message.chat.id
    location = message.text
    job[message.from_user.username]["job_location"] = location
    bot.send_message(chat_id, f"okay {location} is set to be your location")
    start_taking_requirements(chat_id, message)


def register_job_type(message, option):
    """save the job type

    Args:
        message (types.Message): information about the user
        option (string): the option chosen by the user
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Okay {option.data} is the type of your job")
    job[option.from_user.username]["job_type"] = option.data
    bot.send_message(
        chat_id, "What is the format of the job?", reply_markup=job_format_markup()
    )


def register_job_format(message, option):
    """save the job format, then wait for the job requirements

    Args:
        message (types.Message): information about the user
        option (string): the option chosen by the user
    """
    job[option.from_user.username]["job_format"] = option.data
    chat_id = message.chat.id
    if option.data != "remote":
        msg = bot.send_message(
            chat_id,
            f"Since you chose your job to be {option.data}, please write the location of your office:",
        )
        bot.register_next_step_handler(msg, wait_for_job_location)
    else:
        start_taking_requirements(chat_id, message)


def start_taking_requirements(chat_id, message):
    bot.send_message(
        chat_id,
        f"Finally, please add the requirements of your job in the format: requirement description/years of experience\n \
For example, you can write: c++ / 3 to indicate that you need a person with three years of experience in c++",
    )
    requirements[message.chat.username] = []
    wait_for_job_requirements(message)


def register_new_requirement(message):
    """save a new job requirement then wait for another one

    Args:
        message (types.Message): stores the user's information
    """
    chat_id = message.chat.id
    if message.text == "stop adding requirements":
        bot.send_message(
            chat_id,
            "okay got the requirements",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        save_job_to_db(message)
        return
    text = (message.text).split("/")
    if len(text) > 1:
        text[1] = text[1].strip()
    if len(text) != 2:
        bot.send_message(
            chat_id,
            "Please make sure you use the format: requirement / years of experience",
        )
    elif not text[1].isnumeric():
        bot.send_message(chat_id, "Please add the years of experience as a number")
    else:
        requirements[message.chat.username].append(
            {"requirement_description": text[0], "requirement_duration": text[1]}
        )
    wait_for_job_requirements(message)


def wait_for_job_requirements(message):
    """retrieve the job requirment

    Args:
        message (types.Message): stores the user's information
    """
    chat_id = message.chat.id
    msg = bot.send_message(
        chat_id,
        "Add a requirment for your job:",
        reply_markup=stop_requirments_markup(),
    )
    bot.register_next_step_handler(msg, register_new_requirement)


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


def save_job_to_db(message):
    """function to save the retrieved job to the database
    
    Args:
        message (types.Message): information about the sender
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        sql = insert_directory(job[message.from_user.username], "jobs")
        cur.execute(sql + "RETURNING job_id", list(job[message.from_user.username].values()))
        lst = cur.fetchone()
        lst_id = lst[0]
        for element in requirements[message.from_user.username]:
            element["job_id"] = lst_id
            sql = insert_directory(element, "requirements")
            cur.execute(sql, list(element.values()))
        cur.close()
        conn.commit()
        del job[message.from_user.username]
        del requirements[message.from_user.username]
    except psycopg2.DatabaseError as error:
        print(error)


def create_tables():
    """function to create tables in the database
    """
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


if __name__ == "__main__":
    create_tables()
    bot.infinity_polling()
