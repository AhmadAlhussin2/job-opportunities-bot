[![Linter](https://github.com/AhmadAlhussin2/job-opportunities-bot/actions/workflows/pylint.yml/badge.svg)](https://github.com/AhmadAlhussin2/job-opportunities-bot/actions/workflows/pylint.yml)

# Job opportunities bot

## Project structure

![](./static/server-setup.gif)

- ### Main server

    The server is implemented where it should patiently wait for clients to complete their requests.

    For instance, if a client intends to post a job, the server collects essential details such as job title, format, type, and requirements. Subsequently, it  forwards this request block to Nginx .

    The server's sole responsibility lies in forwarding client requests to Nginx; it does not directly send any results to clients. Consequently, it can efficiently process a high volume of requests, and the database manager will transmit the results to clients once they are ready.

- ### wire

    This script is implemented to relay requests from the main server to the Nginx server.

    The functionality of this script resembles a Remote Procedure Call (RPC), as it receives database requests and Telegram chat IDs, forwarding them to the Nginx server.

- ### Nginx server

    To optimize performance, an Nginx server is implemented as a proxy passer and load balancer. This configuration is particularly effective since database operations are significantly more resource-intensive than waiting for new messages.

    The official Nginx image is utilized, along with a customized nginx.conf configuration file. 

    Essentially, the Nginx server routes incoming requests to three distinct database managers, each performing post and retrieve operations within the same database.

- ### Database managers

    The database managers patiently await incoming requests.

    Upon receiving a client's request, they execute the corresponding database operations and directly transmit the results to the client. This approach enhances the server's processing speed since it no longer needs to wait for the results before sending them to clients.

- ### Docker

    The solution employs three Docker images: one for Nginx, one for the database manager, and one for the server. 
    
    Each image contains all the necessary dependencies for the respective files, ensuring portability and ease of deployment.
     

## Usage

The project uses docker compose to install the requirements, run scripts, and install requirements.

So, to run the project locally you need:

- postgres database

    You need to specify the following in `.env` file:

    - __HOST :__ where the database is hosted
    - __PORT :__ port number for database connection
    - __DB_USER :__ username for the database connection
    - __DB_PASSWORD :__ password to connect
    - __DB_NAME :__ name of the created database

    All of those can be easily created in pg-admin 

- wire connection URL

    __WIRE_URL__: in this project we set it up to be `http://localhost:80` (where nginx is configured to listen).

- docker, docker-compose

    In ubuntu it can be done like in the official [docs](https://docs.docker.com/compose/install/)

- The project is configured to run locally in a single machine using localhost with different port number for each component. If you want to test it on different hosts or maybe on different addresses, here are what you need to change:
    
    - __backend block__ in __nginx.conf__: specify the addresses where you want to run database managers.
    - __listening address__ in __nginx.conf__: specify where you want nginx server to listen and it should be same as __WIRE_URL__ mentioned above.
    - __Addresses where database managers are running__: we spcified them as command line arguments provided to the python file by docker-compose. Therefore, either change them in __docker-compose__ or run __database.py__ with command line argument (port number).


## Testing

Testing in the project is not complete yet. Nevertheless, we have unit testing in `/tests` folder.

To run the tests some more variables need to be set in `.env` file. Those variables are:

- __API_ID :__ it can be found in telegram [apps](https://my.telegram.org/apps)
- __API_HASH :__ it also needed to log in to an account and test the bot. It can also be found in telegram [apps](https://my.telegram.org/apps)
