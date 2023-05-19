[![Linter](https://github.com/AhmadAlhussin2/job-opportunities-bot/actions/workflows/pylint.yml/badge.svg)](https://github.com/AhmadAlhussin2/job-opportunities-bot/actions/workflows/pylint.yml)

# Job opportunities bot

## Project structure

![](./static/server-setup.gif)

- ### main server

    The main server _labeled in green in the diagram bellow_ is responsible for recieving clients requests from telegram. We decided to create this server because it is not possible to retrieve the telegram messages from multiple servers _limitation from telegram_. 

    The server in general is responsible for waiting clients to complete their request. For example, if a client wanted to send a request for posting a job, the server will take the job title, format, type, and requirements. Then, the server will forward this request block to __nginx__ server. 

- ### wire

    This python script is create to forward requests from the main server to the nginx server. 

    The functionality of this script is close to RPC (Remote Procedure Call). Basically, it takes the database requests and telegram chat ID and forwards it to the nginx server. 

- ### nginx server

    We decided to make a load balancer with nginx because database operations are much more expensive than waiting for new messages. 

    Basically, the nginx server forward the incoming requests to three different database managers. Nevertheless, all the managers store data in the same database.

- ### database managers

    Perform the database requests from clients, and send the result of those requests to the client

## Usage

The project uses docker compose to install the requirements, run scripts, and install requirements.

So, to run the project locally you need:

- postgres database

    You need to specifit the following in `.env` file:

    - __HOST :__ where the database is hosted
    - __PORT :__ port number for database connection
    - __DB_USER :__ username for the database connection
    - __DB_PASSWORD :__ password to connect
    - __DB_NAME :__ name of the created database

    All of those can be easily created in pg-admin 

- wire connection URL

    __WIRE_URL__: in this project we set it up to be `http://localhost:80`, it can be changed easily

- docker, docker-compose

    In ubuntu it can be done like in the official [docs](https://docs.docker.com/compose/install/)

## Testing

Testing in the project is not complete yet. Nevertheless, we have unit testing in `/tests` folder.

To run the tests some more variables need to be set in `.env` file. Those variables are:

- __API_ID :__ it can be found in telegram [apps](https://my.telegram.org/apps)
- __API_HASH :__ it also needed to log in to an account and test the bot. It can also be found in telegram [apps](https://my.telegram.org/apps)
