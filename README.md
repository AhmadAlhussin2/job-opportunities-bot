[![Linter](https://github.com/AhmadAlhussin2/job-opportunities-bot/actions/workflows/pylint.yml/badge.svg)](https://github.com/AhmadAlhussin2/job-opportunities-bot/actions/workflows/pylint.yml)

# Job opportunities bot

## Server setup

![](./static/server-setup.gif)

## Usage

- Create `.env` file similar to `env.example` with the following variables:
    - __API_KEY__: API key for the telegram bot, you can get one by messaging the [bot father](https://t.me/BotFather)
    - __HOST__: host for postgreSQL database
    - __USER__, __DB_PASSWORD__: credintials for the database

- Create and activate a new virtual environment 

- Install dependencies using requirements.txt 

    ```properties
    pip install -r requirements.txt
    ```

- Run the server

    ```properties
    python server.py
    ```
