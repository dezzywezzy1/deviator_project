# deviator_project

This is a Flask web application running inside a Docker container.

## Getting Started

Follow the steps below to set up and run the application.

### Prerequisites

- [Docker](https://www.docker.com/) installed on your system.

### Clone the Repository

1. Open your terminal.
2. Clone this repository:
   ```bash
   git clone https://github.com/dezzywezzy1/deviator_project.git
   cd deviator_project

### Set up gmail account access for 2 Factor Auth
1. Create gmail app password (your personal gmail account is okay for the purpose of demonstration) \
    [Creating gmail app password](https://support.google.com/mail/answer/185833?hl=en)
2. Create .env file in the project directory with env variables: \
    `MAIL_USERNAME = "your_email"`\
    `MAIL_PASSWORD = "your_app_password"`
### Create SECRET_KEY
1. Generate a token of your choosing and store it in the .env file: \
   `SECRET_KEY = "your_secret_key"`

### Build the Docker image
1. Build image
    ```bash
    docker build -t deviator

### Run the Docker image
1. Run image
    ```bash
    docker run -it -p {your_port}:5000 deviator
2. The terminal will ask you for a few prompts in order to give you access to the site. Make sure you input an email you have access to. 

this app will now be available at `http://localhost:{your_port}`
