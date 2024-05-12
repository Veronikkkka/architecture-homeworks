from confluent_kafka import Producer, Consumer
import json

producer = Producer({'bootstrap.servers': 'kafka:9093'})
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Приклад відправки повідомлення до черги
def reserve_ticket(ticket_id, user_id):
    message = {'ticket_id': ticket_id, 'user_id': user_id}
    
    
    message_json = json.dumps(message)
    
    # Encode the JSON string to bytes
    message_bytes = message_json.encode('utf-8')
    producer.produce("ticket_reservation", message_bytes,)
   
reserve_ticket(1, 'user123')

# Закриваємо з'єднання з Kafka
producer.close()
