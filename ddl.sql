CREATE DATABASE IF NOT EXISTS my_database;
USE my_database;

CREATE TABLE mytable(
            id INT AUTO_INCREMENT PRIMARY KEY,
            symboling VARCHAR(255),
            normalized_losses VARCHAR(255),
            make VARCHAR(255),
            fuel_type VARCHAR(255),
            aspiration VARCHAR(255),
            num_of_doors VARCHAR(255),
            body_style VARCHAR(255),
            drive_wheels VARCHAR(255),
            engine_location VARCHAR(255),
            wheel_base VARCHAR(255),
            length VARCHAR(255),
            width VARCHAR(255),
            height VARCHAR(255),
            curb_weight VARCHAR(255),
            engine_type VARCHAR(255),
            num_of_cylinders VARCHAR(255),
            engine_size VARCHAR(255),
            fuel_system VARCHAR(255),
            bore VARCHAR(255),
            stroke VARCHAR(255),
            compression_ratio VARCHAR(255),
            horsepower VARCHAR(255),
            peak_rpm VARCHAR(255),
            city_mpg VARCHAR(255),
            highway_mpg VARCHAR(255),
            price VARCHAR(255)
);
