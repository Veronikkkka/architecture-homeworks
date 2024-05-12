# from confluent_kafka import Consumer, KafkaError
# import json

# def reservation_consumer():
    
#     consumer = consumer = Consumer({
#     'bootstrap.servers': 'kafka:9093',
#     'group.id': 'my_consumer_group'
#     # 'auto.offset.reset': 'earliest'
#     })
#     consumer.subscribe(['ticket_reservation'])

#     try:
#         while True:
#             msg = consumer.poll(timeout=1.0)
#             if msg is None:
#                 continue
#             # if msg.error():
#             #     if msg.error().code() == KafkaError._PARTITION_EOF:
#             #         # Повідомлення кінця партіції (кінець черги)
#             #         continue
#             #     else:
#             #         # Інша помилка
#             #         print(msg.error())
#             #         break

#             # Обробка отриманого повідомлення
#             else:
#                 message = json.loads(msg.value().decode('utf-8'))
#                 ticket_id = message["ticket_id"]
#                 user_id = message["user_id"]

#                 # Тут ви можете реалізувати логіку резервування квитка
#                 # Наприклад, оновлення статусу квитка у вашій базі даних

#                 print(f"Reserved ticket {ticket_id} for user {user_id}")

#     except KeyboardInterrupt:
#         pass

#     finally:
#         # Завершення роботи споживача
#         consumer.close()

# # Виклик функції споживача
# reservation_consumer()
# import sys, types
# m = types.ModuleType('kafka.vendor.six.moves', 'Mock module')
# setattr(m, 'range', range)
# sys.modules['kafka.vendor.six.moves'] = m
import logging
import json
# from kafka import KafkaConsumer, KafkaProducer
from confluent_kafka import Consumer, Producer
import time
from database_t import SessionLocal, engine
import models
import crud

# Налаштовуємо рівень логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізуємо Kafka consumer та producer
# consumer = KafkaConsumer('comments_requests', bootstrap_servers=['localhost:9093'], group_id='comments_storage_service', api_version=(0,10,1))
# producer = KafkaProducer(bootstrap_servers=['localhost:9093'], api_version=(0,10,1))
# producer = Producer({'bootstrap.servers': 'kafka:9093'})
consumer = Consumer({
    'bootstrap.servers': 'kafka:9093',
    'group.id': 'my_consumer_group', 
    'enable.auto.commit': True
    # 'auto.offset.reset': 'earliest'
})

consumer.subscribe(['ticket_reservation'])
producer = Producer({'bootstrap.servers': 'kafka:9093'})

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#     return db

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
        
        
def process_message(msg, db = SessionLocal()):
    msg = dict(json.loads(msg.value().decode('utf-8')))
    ticket_id = msg['ticket_id']
    db_ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        return "Ticket not found"
    
    if db_ticket.status != "available":
        return "Ticket is not available"
    
    user_id = msg['user_id']
    user = crud.get_user(db, user_id)
    if not user:
        return "User not found"
    
    db_ticket.status = "reserved"
    db_ticket.user_id = user_id
    db.commit()
    return f"Succes: Ticket : {db_ticket}"

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        # # Розпаковуємо повідомлення
        # # logger.info(f"Comment: {msg}"*30)
        if msg != None:
            logger.info(f"Saved comment: {msg.value().decode('utf-8')}")
            logger.info("Proccessimg...")
            result = process_message(msg)
            logger.info("Result ____  " + str(result))
            result = json.dumps(result)
            result = result.encode('utf-8')
            producer.produce('reservation_response', result, callback = delivery_report)
            producer.poll(0)
            producer.flush() 
            
        #     print(f"Received message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    print("ERROr ")
finally:
    consumer.close()
