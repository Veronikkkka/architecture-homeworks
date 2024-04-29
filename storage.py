# import sys, types
# m = types.ModuleType('kafka.vendor.six.moves', 'Mock module')
# setattr(m, 'range', range)
# sys.modules['kafka.vendor.six.moves'] = m
import logging
import json
# from kafka import KafkaConsumer, KafkaProducer
from confluent_kafka import Producer, Consumer
import time

# Налаштовуємо рівень логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізуємо Kafka consumer та producer
# consumer = KafkaConsumer('comments_requests', bootstrap_servers=['localhost:9093'], group_id='comments_storage_service', api_version=(0,10,1))
# producer = KafkaProducer(bootstrap_servers=['localhost:9093'], api_version=(0,10,1))
producer = Producer({'bootstrap.servers': 'kafka:9093'})
consumer = Consumer({
    'bootstrap.servers': 'kafka:9093',
    'group.id': 'my_consumer_group'
    # 'auto.offset.reset': 'earliest'
})

consumer.subscribe(['comments_requests'])

# Структура даних для зберігання коментарів
comments_storage = {}

# Функція для збереження коментарів
def save_comment(comment):
    # comment = dict(comment)
    logger.info(f"{type(comment)}")
    userId = comment["userId"]
    if userId in comments_storage:
        comments_storage[userId].append(comment)
    else:
        comments_storage[userId] = [comment]
    print(comments_storage)

# Функція для отримання коментарів за userId
def get_comments_by_userId(userId):
    if userId in comments_storage:
        return comments_storage[userId]
    else:
        return []


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# Функція для обробки отриманих повідомлень
def process_message(message):
    try:
        # Розпаковуємо повідомлення
        # comment = json.loads(message.value.decode('utf-8'))
        comment = json.loads(msg.value().decode('utf-8'))
        # Якщо повідомлення містить коментар, зберігаємо його
        if "comment" in comment and "userId" in comment:
            save_comment(comment)
            logger.info(f"Saved comment: {comment}")
        # Якщо повідомлення містить запит на отримання коментарів за userId, відправляємо відповідь
        elif "get_comments_by_userId" in comment and "userId" in comment:
            userId = comment["userId"]
            comments = get_comments_by_userId(userId)
            response_message = {"userId": userId, "comments": comments}
            # producer.send('comments_responses', value=json.dumps(response_message).encode('utf-8'))
            
            producer.produce('comments_responses', value=json.dumps(response_message).encode('utf-8'), callback=delivery_report)
            producer.poll(0)
            # time.sleep(0.1)
            producer.flush() 
            
            logger.info(f"Sent response for userId {userId}: {response_message}")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

# # Головний цикл обробки повідомлень
# for message in consumer:
#     process_message(message)

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        # Розпаковуємо повідомлення
        # logger.info(f"Comment: {msg}"*30)
        if msg:
            logger.info(f"Saved comment: {msg.value().decode('utf-8')}")
            process_message(msg)
            
            print(f"Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    print("ERROr ")
finally:
    consumer.close()