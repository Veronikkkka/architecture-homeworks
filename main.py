# import time
from confluent_kafka import Producer, Consumer

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# comments_storage = {}

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# def send_data_to_kafka(filename, topic_name, p):
#     print("HERE2")
#     p.produce(topic_name, b"try", callback=delivery_report)
#     p.poll(0)
#     time.sleep(0.1)  # To achieve 10 messages per second
#     p.produce(topic_name, b"try_another", callback=delivery_report)
#     p.poll(0)
#     time.sleep(0.1) 
#     p.flush()
    

producer = Producer({'bootstrap.servers': 'kafka:9093'})
# send_data_to_kafka('sample.csv', 'comments_responses', producer)

consumer = Consumer({
    'bootstrap.servers': 'kafka:9093',
    'group.id': 'my_consumer_group'
    # 'auto.offset.reset': 'earliest'
})

consumer.subscribe(['comments_responses'])

from fastapi import FastAPI, HTTPException, Query
# import requests
# import sys, types
import json
# m = types.ModuleType('kafka.vendor.six.moves', 'Mock module')
# setattr(m, 'range', range)
# sys.modules['kafka.vendor.six.moves'] = m
# from kafka import KafkaProducer, KafkaConsumer
# from kafka.errors import KafkaError
# import uvicorn

# Ініціалізуємо FastAPI додаток
app = FastAPI()

# Ініціалізуємо Kafka producer
# producer = KafkaProducer(bootstrap_servers=['kafka:9092'], api_version=(0,10,1))
# consumer = KafkaConsumer('comments_responses', bootstrap_servers=['kafka:9092'], group_id='comments_handler_service')


@app.post("/comments")
async def add_comment(comment: str, userId: int):
    message = {"comment": comment, "userId": userId}
    
    # Serialize the dictionary to JSON string
    message_json = json.dumps(message)
    
    # Encode the JSON string to bytes
    message_bytes = message_json.encode('utf-8')
    
    # Send the encoded message to Kafka
    # producer.send("comments_requests", value=message_bytes)
    producer.produce("comments_requests", message_bytes, callback=delivery_report)
    return "Success"


@app.get("/comments")
async def get_comments_by_userId(userId: int = Query(..., description="User ID")):
    try:
        request_message = {"get_comments_by_userId": True, "userId": userId}
        # producer.send("comments_requests", json.dumps(request_message).encode('utf-8'))
        producer.produce("comments_requests", json.dumps(request_message).encode('utf-8'), callback=delivery_report)
        # Читаємо відповідь з коментарями з топіка "comments_responses"
        # return "Success"
        import time
        time.sleep(1)
        message = consumer.poll(timeout=1.0)
        # for message in consumer:
        response = json.loads(message.value().decode('utf-8') )
        logger.info(f"infa {response}")
        
        if response["userId"] == userId:
            return response["comments"]
        
        elif response:
            return response["comments"]
        else:
            raise HTTPException(status_code=404, detail="No comments found for the given user ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error while fetching comments")
    
    
# @app.post("/commenttwo")
# async def get2():
#     producer.send('try', b'first')
#     return "HERE"