from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup
from constants import *


def job_type_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        *[InlineKeyboardButton(job, callback_data=job.lower()) for job in JOB_TYPES]
    )
    return markup


def job_format_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(*[InlineKeyboardButton(job, callback_data=job) for job in JOB_FORMATS])
    return markup


def stop_requirments_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(InlineKeyboardButton("stop adding requirements", callback_data="stop"))
    return markup
