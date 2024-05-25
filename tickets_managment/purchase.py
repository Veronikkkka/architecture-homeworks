import logging
import json
# from kafka import KafkaConsumer, KafkaProducer
from confluent_kafka import Consumer, Producer
import time
from database_t import SessionLocal, engine
import models
import crud


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# producer = Producer({'bootstrap.servers': 'kafka:9093'})
consumer = Consumer({
    'bootstrap.servers': 'kafka:9093',
    'group.id': 'my_consumer_group'
    # 'auto.offset.reset': 'earliest'
})

consumer.subscribe(['ticket_purchase'])
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
        
        
def process_message(msg, db=SessionLocal()):
    msg = dict(json.loads(msg.value().decode('utf-8')))
    ticket_id = msg['ticket_id']
    purchase_id = msg['purchase_id']
    
    db_ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        return {"purchase_id": purchase_id, "status": "failure", "reason": "Ticket not found"}
    
    if db_ticket.status != "available":
        return {"purchase_id": purchase_id, "status": "failure", "reason": "Ticket not available"}
    
    user_id = msg['user_id']
    user = crud.get_user(db, user_id)
    if not user:
        return {"purchase_id": purchase_id, "status": "failure", "reason": "User not found"}
    
    db_ticket.status = "sold"
    db_ticket.user_id = user_id
    db.commit()
    
    return {"purchase_id": purchase_id, "status": "success", "ticket": db_ticket.ticket_id, "user": user_id}

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg:
            logger.info(f"Received message: {msg.value().decode('utf-8')}")
            result = process_message(msg, db=SessionLocal())
            logger.info(f"Processing result: {result}")
            result_json = json.dumps(result)
            result_bytes = result_json.encode('utf-8')
            producer.produce('purchase_response', result_bytes, callback=delivery_report)
            producer.poll(0)
            producer.flush()
except KeyboardInterrupt:
    logger.error("Process interrupted by user")
finally:
    consumer.close()