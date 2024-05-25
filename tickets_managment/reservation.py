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

consumer = Consumer({
    'bootstrap.servers': 'kafka:9093',
    'group.id': 'my_consumer_group', 
    'enable.auto.commit': True
    # 'auto.offset.reset': 'earliest'
})

consumer.subscribe(['ticket_reservation'])
producer = Producer({'bootstrap.servers': 'kafka:9093'})


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
        
        
def process_message(msg, db = SessionLocal()):
    msg = dict(json.loads(msg.value().decode('utf-8')))
    ticket_id = msg['ticket_id']
    reservation_id = msg['reservation_id']
    
    db_ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        return {"reservation_id": reservation_id, "status": "failure", "reason": "Ticket not found"}
    
    if db_ticket.status != "available":
        return {"reservation_id": reservation_id, "status": "failure", "reason": "Ticket not available"}
    
    user_id = msg['user_id']
    user = crud.get_user(db, user_id)
    if not user:
        return {"reservation_id": reservation_id, "status": "failure", "reason": "User not found"}
    
    db_ticket.status = "reserved"
    db_ticket.user_id = user_id
    db.commit()
    
    return {"reservation_id": reservation_id, "status": "success", "ticket": db_ticket.ticket_id, "user": user_id}

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg:
            logger.info(f"Received message: {msg.value().decode('utf-8')}")
            result = process_message(msg, db=SessionLocal())
            logger.info(f"Processing result: {result}")
            result_json = json.dumps(result)
            result_bytes = result_json.encode('utf-8')
            producer.produce('reservation_response', result_bytes, callback=delivery_report)
            producer.poll(0)
            producer.flush()
except KeyboardInterrupt:
    logger.error("Process interrupted by user")
finally:
    consumer.close()