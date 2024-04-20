# Homework 6: add cache Redis

Author: Veronika

## 📝 What does this MR do?

I introduced caching mechanisms to improve the performance of the application. This includes caching event details, descriptions, and reviews to reduce database queries and improve response times.To achieve this, I made alterations to several endpoints, encompassing GET, POST, PUT, and DELETE operations for each respective table (event, reviews, description). Additionally, I introduced a new endpoint designed to consolidate all pertinent information about an event. This includes details about the event itself, its associated description, and any reviews it may have garnered.

## 🏃‍♂️ How to run and Results

With caching implemented, response times for retrieving event details, descriptions, and reviews should be significantly faster, as fewer database queries will be required.

All screenshots you can see in Result.docx in this repo

### How to run the application


1. Clone the repository

   `git clone hw6`

2. Go to directory `hw6`
   `cd hw6`

3. Run this command to ...
   `docker-compose up --build`
   ![image_command_result.png](https://gitlab.com/architectureit/architecture-Shevtsova/-/blob/hw6/res.png)


