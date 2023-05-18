""" testing file """
import os
import time
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
TOKEN = os.environ['API_KEY']

client = TelegramClient('session', API_ID, API_HASH)

async def _start():
    await client.send_message('@jobs_for_you_bot', '/find_job')
    timeout = time.time() + 5
    while True:
        new_msg = await client.get_messages('@jobs_for_you_bot', limit=1)
        if new_msg[0].message == 'What type of jobs are you interested in?':
            print(new_msg[0])
            break
        if time.time() > timeout:
            assert 0,"the bot is not responding"
    assert new_msg[0].message=='What type of jobs are you interested in?',\
            "got an unexpected response from the bot"

async def _click_type():
    lst_msg = await client.get_messages('@jobs_for_you_bot', limit=1)
    timeout = time.time() + 5
    await lst_msg[0].click(0)
    while True:
        new_msg = await client.get_messages('@jobs_for_you_bot', limit=1)
        if new_msg[0].message == 'Okay, and what is your preferable format?':
            print(new_msg[0])
            break
        if time.time() > timeout:
            assert 0,"the bot is not responding"
    assert new_msg[0].message=='Okay, and what is your preferable format?',\
            "got an unexpected response from the bot"

async def _click_format():
    lst_msg = await client.get_messages('@jobs_for_you_bot', limit=1)
    timeout = time.time() + 5
    await lst_msg[0].click(1)
    while True:
        new_msg = await client.get_messages('@jobs_for_you_bot', limit=1)
        if new_msg[0].message == 'Add a skill:':
            print(new_msg[0])
            break
        if time.time() > timeout:
            assert 0,"the bot is not responding"
    assert new_msg[0].message=='Add a skill:',\
            "got an unexpected response from the bot"

def _wire(test_func):
    with client:
        client.loop.run_until_complete(test_func())

def test_start():
    """ test function to see if starting the bot is working or not
    """
    _wire(_start)

def test_type():
    """ test function to see if clicking on the job'a type is working or not
    """
    _wire(_click_type)

def test_format():
    """ test function to see if clicking on the job'a format is working or not
    """
    _wire(_click_format)
