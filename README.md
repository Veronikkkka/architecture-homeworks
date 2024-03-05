# Homework 3: 🐳 Getting started with Docker

Author: Veronika

## 📝 What does this MR do?
This MR implements the Docker task using MySQL and Python. The Python script connects to a MySQL database, creates a table using DDL scripts, and inserts data from an internet text file. The code, DDL script, Dockerfile, and docker-compose file are included. The MySQL database and Python program run in separate containers, demonstrating successful execution through provided screenshots.

The Python script establishes a connection to the MySQL database hosted on the "mysql" service and creates a table by executing DDL scripts from the "ddl.sql" file. Data is then fetched from an internet file, parsed, and inserted into the MySQL table.

The Dockerfile is configured to use the Python 3.8-slim image, set the working directory, copy the project files, and install dependencies from the "requirements.txt" file. The command runs the Python script when the container starts.

The docker-compose.yml file defines two services: "db" for the MySQL database and "app" for the Python application. The "app" service depends on the "db" service, ensuring proper startup order. Both services are connected to an external bridge network named "mynetwork."


## 🏃‍♂️ Results

Describe the specific results or outcomes of the application's execution.
Provide any relevant screenshots, logs, or data to illustrate the results.

[result1](https://gitlab.com/architectureit/architecture-Shevtsova/-/blob/homework3/result1.png?ref_type=heads)
[result2](https://gitlab.com/architectureit/architecture-Shevtsova/-/blob/homework3/result2.png?ref_type=heads)
[result3](https://gitlab.com/architectureit/architecture-Shevtsova/-/blob/homework3/result3.png?ref_type=heads)
[result4](https://gitlab.com/architectureit/architecture-Shevtsova/-/blob/homework3/result4.png?ref_type=heads)


### How to run the application



❗️ It is **mandatory** to illustrate results, otherwise it will lead to _points deduction_.❗️

1. Clone the repository

   `git clone https://gitlab.com/your-username/architecture-Shevtsova.git -b homework3`

2. Go to directory `{cd architecture-Shevtsova}`
   `cd architecture-Shevtsova`

3. Run this command to ...
   `./build.sh`
   `docker-compose up -d` * 2
   ![result1](https://gitlab.com/architectureit/architecture-Shevtsova/-/blob/homework3/result1.png?ref_type=heads)

