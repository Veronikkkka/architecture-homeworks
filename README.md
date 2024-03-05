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




### How to run the application

🦾 [ Example – modify for your case ] 🦾

❗️ It is **mandatory** to illustrate results, otherwise it will lead to _points deduction_.❗️

1. Clone the repository

   `git clone {your_repo_name}`

2. Go to directory `{your_hw_directory}`
   `cd {your_hw_directory}`

3. Run this command to ...
   `{command_to_run}`
   ![image_command_result.png]({your_image_path})

## 🎀 Additional Notes

Add any additional information here, which you consider important to note, especially if it is related to homework structure, what can be improved, and what you has struggles with.
