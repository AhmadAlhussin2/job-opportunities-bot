"""generate general markups for the server"""
import telebot
from constants import JOB_FORMATS, JOB_TYPES


def job_type_markup():
    """create marckup for selecting the jobtype

    Returns:
        types.Markup: a markup for selecting the jobtype
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        *[
            telebot.types.InlineKeyboardButton(job, callback_data=job.lower())
            for job in JOB_TYPES
        ]
    )
    return markup


def job_format_markup():
    """a markup for settting the job format

    Returns:
        types.Markup: a markup to choose the job format
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        *[
            telebot.types.InlineKeyboardButton(job, callback_data=job)
            for job in JOB_FORMATS
        ]
    )
    return markup


def stop_requirments_markup():
    """a stopping buttonm used to stop asking for requirements

    Returns:
        types.Markup: a markup that stop the bot from asking for new requirements
    """
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.InlineKeyboardButton(
            "stop adding requirements", callback_data="stop"
        )
    )
    return markup


def stop_skills_markup():
    """a stopping buttonm used to stop asking for skills

    Returns:
        types.Markup: a markup that stop the bot from asking for new skills
    """
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        telebot.types.InlineKeyboardButton("stop adding skills", callback_data="stop")
    )
    return markup


def job_find_format_markup():
    """markup to set the job format

    Returns:
        types.Markup: a markup to set the job format
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        *[
            telebot.types.InlineKeyboardButton(job, callback_data="find_" + job)
            for job in JOB_FORMATS
        ]
    )
    return markup


def job_find_type_markup():
    """markup to find the job type

    Returns:
        types.Markup: a markup to set the job type
    """
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        *[
            telebot.types.InlineKeyboardButton(job, callback_data="find_" + job.lower())
            for job in JOB_TYPES
        ]
    )
    return markup
