# WEBSUB HUB

This project is an implementation of a websub hub for the ethereum channel based on libtrustbridge.

#### COMPONENTS:
1. ```localstack``` - used for local aws services emulation
  * Repos:
    1. ```channel``` - queue, used for communication with ```ethereum channel api```.
    JSON messages format:
    ```json
        {
            "id": "<transaction-hash>",
            "status": "received",
            "message": {
                "receiver": "<required>"
                ...
            }
        }
    ```
    1. ```delivery_outbox``` - queue, contains internal jobs.
    1. ```notifications``` -  queue, contains internal jobs.
    1. ```subscriptions``` - bucket, contains websub subscriptions data.
1. ```websub-hub```:
  1. ```websub api``` - used for subscribe/unsubscribe operations via HTTP requests. It uses ```subscriptions``` repo to store data. ```websub-hub/api.yml``` - API specs. 
  1. ```new messages observer processor``` - processor that listens for new message notifications in ```channel``` repo. It initiates websub notifications delivery process by sending messages that passed ```message.receiver``` filtration to the ```notifications``` repo.
  1. ```callback spreader processor``` - intermediary processor between ```new messages observer``` and ```callback delivery``` processors. It splits single websub notification into jobs for the ```callback delivery``` processor. So, each subscriber will get its own delivery job.
  1. ```callback delivery processor``` - performs notification delivery.

#### CONFIGURATION(ENV):
* ```IGL_<UPPERCASE_REPO_NAME>_REPO_USE_SSL``` - 1/0, True/False
* ```IGL_<UPPERCASE_REPO_NAME>_REPO_REGION``` - string
* ```IGL_<UPPERCASE_REPO_NAME>_REPO_HOST``` - string
* ```IGL_<UPPERCASE_REPO_NAME>_REPO_PORT``` - string
* ```IGL_<UPPERCASE_REPO_NAME>_REPO_ACCESS_KEY``` - string
* ```IGL_<UPPERCASE_REPO_NAME>_REPO_SECRET_KEY``` - string
* ```SERVICE_NAME``` - name of the main logger
* ```SERVER_NAME``` - required, name of the flask server, domain name or ip, used to dynamically form a hub url
* ```ENDPOINT``` - required, used to filter messages, ```new messages observer processor``` should not notify about messages of other receivers, but only about ones that addressed to it.
* ```SENTRY_DSN``` - enables sentry logging if set.
* ```ICL_LOG_FORMATTER_JSON``` - enables json logging integration, 1/0, True/False

#### WORKFLOW:
1. A subscription created using ```websub api```
1. ```ethereum channel``` puts a new message notification into ```channel``` repo
1. ```new messages observer processor``` picks the notification from ```channel``` repo
1. ```if ENDPOINT == notification.message.receiver``` the notification passed into ```notifications``` repo.
1. ```callback spreader processor``` picks the notification from ```notifications``` repo. It gets list of the subscribers that listen for the ```jurisdiction.<ENDPOINT>``` topic and creates a callback delivery jobs for each. The processor puts these jobs into ```delivery_outbox``` repo.
1. ```callback delivery processor``` picks the jobs from ```delivery_outbox``` repo. It tries to send the new message notification to specified subscription callback. It has 3 attempts to deliver the notification, otherwise job gets removed from ```delivery_outbox``` repo.
