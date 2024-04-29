#!/bin/bash

# Create a network
docker network create kafka-network

# Run Zookeeper
docker run -d --net=kafka-network --name=zookeeper -e ZOOKEEPER_CLIENT_PORT=2181 confluentinc/cp-zookeeper:latest

# Run Kafka
docker run -d --net=kafka-network --name=kafka -p 9092:9092 -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 confluentinc/cp-kafka:latest

# Create topic
# docker run --net=kafka-network -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 --rm confluentinc/cp-kafka:latest kafka-topics --create --topic tweets --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:2181
# docker run --net=kafka-network -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 --rm confluentinc/cp-kafka:latest kafka-topics --create --topic tweets --partitions 1 --replication-factor 1 --if-not-exists --bootstrap-server kafka:9092
docker run --net=kafka-network -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 --rm confluentinc/cp-kafka:latest kafka-topics --create --topic comments_requests --partitions 1 --replication-factor 1 --if-not-exists --bootstrap-server kafka:9092
docker run --net=kafka-network -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 --rm confluentinc/cp-kafka:latest kafka-topics --create --topic comments_responses --partitions 1 --replication-factor 1 --if-not-exists --bootstrap-server kafka:9092
