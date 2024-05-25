from queue import Queue
import time

class PurchaseModule:
    def __init__(self, message_queue):
        self.message_queue = message_queue

    def buy_ticket(self, ticket_id, user_id):
        # Логіка купівлі квитка
        # Наприклад, перевірка статусу та купівля квитка для користувача
        print(f"Ticket {ticket_id} bought by user {user_id}")
        # Повідомлення про купівлю квитка
        message = {"ticket_id": ticket_id, "user_id": user_id, "action": "buy"}
        self.message_queue.put(message)
        return "Ticket bought successfully"

