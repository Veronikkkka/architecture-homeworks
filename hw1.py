import mysql.connector
from mysql.connector import Error
import requests
from io import StringIO
import os
import csv

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host= "mysql",
            user="root",
            password="myrootpassword"
            # database="my_database"            
        )
        if connection.is_connected():
            print(f"Connected to the  database.")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def create_table(connection):
    with open("ddl.sql", "r") as file:
        cursor = connection.cursor()
        sql_text = file.read()
        cursor.execute(sql_text)
        


def insert_data(cursor, data):
    try:
        
        # print(data[0])
        insert_data_query = """
        INSERT INTO mytable (
            symboling, normalized_losses, make, fuel_type, aspiration, num_of_doors,
            body_style, drive_wheels, engine_location, wheel_base, length, width,
            height, curb_weight, engine_type, num_of_cylinders, engine_size,
            fuel_system, bore, stroke, compression_ratio, horsepower, peak_rpm,
            city_mpg, highway_mpg, price
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """
        cursor.execute(insert_data_query, data)
        cursor.fetchall()
        print("Data inserted successfully.")
    except Error as e:
        print(f"Error1: {e}")

def get_file(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to download the file. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading the file: {e}")
        return None


def fetch_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch file. Status code: {response.status_code}")


def main():
    connection = create_database_connection()
    if connection:
        
        create_table(connection)

        # file_content = get_file("https://github.com/Opensourcefordatascience/Data-sets/blob/master/automotive_data.csv")
        # file = file_content.strip().split('\n')
        # print(file)
        connection_ = mysql.connector.connect(
            host= "mysql",
            user="root",
            password="myrootpassword",
            database="my_database"            
        )        
        cursor2 = connection_.cursor()
        csv_data = fetch_file("https://raw.githubusercontent.com/Opensourcefordatascience/Data-sets/master/automotive_data.csv")
        csv_data = csv_data.strip().split('\n')
        # print(csv_data)
        if csv_data: 
            # print("HERE2")      
            csv_reader = csv.reader(csv_data)
            next(csv_reader) 
            # print(header)    
            # file = csv.reader(file)
            # insert_data(connection, file)
            for row_ in csv_reader:
                data = tuple(row_)
                print(data)
                insert_data(cursor2, data)

        connection_.commit()
        connection_.close()

if __name__ == "__main__":
    main()
