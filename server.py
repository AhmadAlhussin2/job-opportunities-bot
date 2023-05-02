import telebot
import os
from dotenv import load_dotenv
from markups import *
from database import create_tables, save_job_to_db, fetch_jobs, fetch_requirements
from constants import *
from telebot import types


load_dotenv()
API_KEY = os.environ["API_KEY"]

bot = telebot.TeleBot(API_KEY)
global job, requirements, skills
job = {}
requirements = {}
skills = {}


@bot.message_handler(commands=["post_job"])
def post_job(message):
    """post job function to handle recieveing job details and adding them to the databse

    Args:
        message (types.Message): a command to initiate the process (post_job for now)
    """
    bot.send_message(
        message.chat.id,
        "Thanks for using job opportunities bot\nTo post a new job please answer the following questions:",
    )
    job[message.from_user.username] = {}
    msg = bot.send_message(message.chat.id, "What is the job title?")
    bot.register_next_step_handler(msg, wait_for_job_name)


@bot.message_handler(commands=["find_job"])
def find_job(message):
    """find jobs related to the candidate's skills

    Args:
        message (types.Message): a command to initiate the process (find_job)
    """
    bot.send_message(
        message.chat.id,
        "Thanks for using job opportunities bot\nTo find opportunities please answer the following questions:",
    )
    skills[message.from_user.username] = {}
    msg = bot.send_message(
        message.chat.id,
        "What type of jobs are you interested in?",
        reply_markup=job_find_type_markup(),
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """function to handle all the callbacks from custom keyboards

    Args:
        call (types.CallbackQuery): the callback data to be handled
    """
    if call.data in (job.lower() for job in JOB_TYPES):
        register_job_type(call.message, call)
    elif call.data in ("find_" + job.lower() for job in JOB_TYPES):
        add_job_type_filter(call.message, call)
    elif call.data in JOB_FORMATS:
        register_job_format(call.message, call)
    elif call.data in ("find_" + job for job in JOB_FORMATS):
        add_job_format_filter(call.message, call)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


def take_job_location(message, next_step, storage):
    storage["job_location"] = message.text
    next_step(message.chat.id, message)

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


def add_job_type_filter(message, option):
    chat_id = message.chat.id
    skills[option.from_user.username]["job_type"] = option.data[5:]
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message.message_id,
        text="Okay, and what is your preferable format?",
        reply_markup=job_find_format_markup(),
    )


def add_job_format_filter(message, option):
    chat_id = message.chat.id
    skills[option.from_user.username]["job_format"] = option.data[5:]
    if option.data != "find_remote":
        msg = bot.send_message(chat_id, "Okay, then please send your location")
        bot.register_next_step_handler(
            msg,
            lambda msg: take_job_location(
                msg, start_taking_skills, skills[option.from_user.username]
            ),
        )
    else:
        start_taking_skills(chat_id, message)


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
        bot.register_next_step_handler(
            msg,
            lambda msg: take_job_location(
                msg, start_taking_requirements, job[option.from_user.username]
            ),
        )
    else:
        start_taking_requirements(chat_id, message)


def start_taking_skills(chat_id, message):
    bot.send_message(
        chat_id,
        "Now please add some of your skills. You can add them in the format: skill description / years of experience\n\
For example, you can write: c++ / 3 to indicate that you have three years of experience in c++",
    )
    skills[message.chat.username]["skills"] = []
    wait_for_skills(message)


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
        save_job_to_db(message, job, requirements)
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


def register_new_skill(message):
    chat_id = message.chat.id
    if message.text == "stop adding skills":
        bot.send_message(
            chat_id,
            "okay got the skills",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        jobs = fetch_jobs(message,skills)
        for i in jobs:
            job_offer = i[1]+"\n"
            job_offer += i[2]
            if i[2] != 'remote':
                job_offer += f" ({i[4]})"
            job_offer+="\n\n"
            job_offer+="About the job\n"
            job_offer+=f"Job title: {i[1]}\n"
            job_offer+=f"Job type: {i[3]}\n"
            job_offer+=f"Job format: {i[2]}"
            if i[2] != 'remote':
                job_offer += f" ({i[4]})"
            job_offer+="\n\n"
            job_offer+="Requirements:"
            requirement_list = fetch_requirements(i[0])
            print(requirement_list)
            for j in requirement_list:
                job_offer += f"\n- {j[0]} / {j[1]} year"
                if j[1] != 1:
                    job_offer += "s"
            
            bot.send_message(chat_id,job_offer)
        return
    text = (message.text).split("/")
    if len(text) > 1:
        text[1] = text[1].strip()
    if len(text) != 2:
        bot.send_message(
            chat_id,
            "Please make sure you use the format: skill / years of experience",
        )
    elif not text[1].isnumeric():
        bot.send_message(chat_id, "Please add the years of experience as a number")
    else:
        skills[message.chat.username]["skills"].append(
            {"skill_description": text[0], "skill_duration": text[1]}
        )
    wait_for_skills(message)


def wait_for_skills(message):
    chat_id = message.chat.id
    msg = bot.send_message(
        chat_id,
        "Add a skill:",
        reply_markup=stop_skills_markup(),
    )
    bot.register_next_step_handler(msg, register_new_skill)


if __name__ == "__main__":
    create_tables()
    bot.infinity_polling()
