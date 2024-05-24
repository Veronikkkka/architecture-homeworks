import models
import schemas2 as schemas
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException
from datetime import date


def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.event_id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Event).offset(skip).limit(limit).all()


def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Отримуємо id створеної події
    event_id = db_event.event_id
    
    # Додаємо виконавців до таблиці event_performer_association
    for performer_id in event.performers:
        db.execute(models.event_performer_association.insert().values(event_id=event_id, performer_id=performer_id))
    
    return db_event


def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()


def get_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ticket).offset(skip).limit(limit).all()


def create_ticket(db: Session, ticket: schemas.TicketCreate, event_id: int, user_id: int):
    db_ticket = models.Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_performer(db: Session, performer_id: int):
    return db.query(models.Performer).filter(models.Performer.performer_id == performer_id).first()


def get_performers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Performer).offset(skip).limit(limit).all()


def create_performer(db: Session, performer: schemas.PerformerCreate):
    db_performer = models.Performer(**performer.dict())
    db.add(db_performer)
    db.commit()
    db.refresh(db_performer)
    
    # Отримуємо id створеного виконавця
    performer_id = db_performer.performer_id
    
    # Додаємо події до таблиці event_performer_association
    for event_id in performer.events:
        db.execute(models.event_performer_association.insert().values(event_id=event_id, performer_id=performer_id))
    
    return db_performer

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_tickets(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user.tickets
    return []


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_event(db: Session, event_id: int, event: schemas.EventCreate):
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id).first()
    if db_event:
        db_event.name = event.name
        db_event.date = event.date
        db_event.time = event.time
        db_event.venue = event.venue
        db_event.ticket_quantity = event.ticket_quantity
        db_event.performers = []
            # Оновлення таблиці event_performer_association (якщо потрібно)

        db.commit()
        db.refresh(db_event)
        return db_event
    else:
        return None
    
def update_performer(db: Session, performer_id: int, performer: schemas.PerformerCreate):
    db_performer = db.query(models.Performer).filter(models.Performer.performer_id == performer_id).first()
    if db_performer:
        db_performer.first_name = performer.first_name
        db_performer.last_name = performer.last_name
        db_performer.events = []
        db.commit()
        db.refresh(db_performer)
        return db_performer
    else:
        return None    

def update_user(db: Session, user_id: int, user_update: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user_update.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None



def add_performer_to_event(db: Session, event_id: int, performer_id: int):
    # Отримуємо об'єкт події за її ідентифікатором
    db_event = db.query(models.Event).filter(models.Event.event_id == event_id).first()
    
    # Отримуємо об'єкт виконавця за його ідентифікатором
    db_performer = db.query(models.Performer).filter(models.Performer.performer_id == performer_id).first()
    
    # Перевіряємо, чи обидва об'єкти існують
    if db_event is None or db_performer is None:
        return None
    
    # Додаємо виконавця до списку виконавців події
    db_event.performers.append(db_performer)
    
    # Зберігаємо зміни в базі даних
    db.commit()
    
    # Повертаємо оновлений об'єкт події
    return db_event


def get_events_by_date(db: Session) -> list:
    # Calculate the date two months from now
    two_months_from_now = datetime.now() + timedelta(days=60)

    # Query events happening in the next two months
    events = db.query(models.Event).filter(models.Event.date >= datetime.now()).filter(models.Event.date <= two_months_from_now).all()
    return events

def get_events_with_sold_out_tickets(db: Session) -> list:
    events = (
        db.query(models.Event)
        .join(models.Ticket, models.Event.event_id == models.Ticket.event_id)
        .group_by(models.Event.event_id, models.Event.name, models.Event.date, models.Event.time, models.Event.venue, models.Event.ticket_quantity)
        .having(func.count(models.Ticket.ticket_id) >= models.Event.ticket_quantity)
    ).all()

    return events

def reserve_ticket(db: Session, ticket_id: int, user_id: int) -> models.Ticket:
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if ticket.status == "sold":
        raise HTTPException(status_code=400, detail="Ticket is already sold")

    if ticket.status == "reserved":
        raise HTTPException(status_code=400, detail="Ticket is already reserved")

    # Перевіряємо, чи знайдено квиток та чи його статус "available"
    if ticket and ticket.status == "available":
        # Змінюємо користувача та статус квитка
        ticket.user_id = user_id
        ticket.status = "reserved"  # Змінюємо статус на "reserved"
        db.commit()  # Зберігаємо зміни в базі даних
        db.refresh(ticket)  # Оновлюємо об'єкт квитка в базі даних
    return ticket

def get_users_reserved_tickets_for_event(db: Session, event_id: int):
    # Отримуємо список квитків, які відповідають заданому event_id
    event_tickets = db.query(models.Ticket).filter(models.Ticket.event_id == event_id).all()

    # Фільтруємо список, залишаючи лише квитки зі статусом "reserved"
    reserved_tickets = [ticket for ticket in event_tickets if ticket.status == "reserved"]

    # Отримуємо список унікальних користувачів, які мають зарезервовані квитки на подію
    unique_reserved_users = db.query(models.User).filter(models.User.id.in_(ticket.user_id for ticket in reserved_tickets)).all()

    return unique_reserved_users

def get_tickets_for_event(db: Session, event_id: int, date: date):
    # Отримуємо дату в форматі datetime з початком дня (00:00:00)
    start_of_day = datetime.combine(date, datetime.min.time())
    # Отримуємо дату в форматі datetime з кінцем дня (23:59:59)
    end_of_day = datetime.combine(date, datetime.max.time())

    # Запит до бази даних для отримання квитків для певної події на задану дату
    tickets = (
        db.query(models.Ticket)
        .join(models.Event)
        .filter(
            models.Event.event_id == event_id,
            models.Event.date >= start_of_day,
            models.Event.date <= end_of_day
        )
        .all()
    )
    return tickets

def get_performers_with_events(db: Session) -> list[models.Performer]:
    return db.query(models.Performer).join(models.event_performer_association).all()

def get_tickets_for_visitor(db: Session, user_id: int) -> list[models.Ticket]:
    return db.query(models.Ticket).filter(models.Ticket.user_id == user_id).all()

def purchase_tickets(db: Session, user_id: int, event_id: int, ticket_id: int) -> bool:
    try:
        available_tickets = (
            db.query(models.Ticket)
            .filter(models.Ticket.ticket_id.in_(ticket_id))
            .filter(models.Ticket.status == "available")
            .all()
        )

        # Якщо кількість доступних квитків не дорівнює кількості обраних квитків,
        # то повертаємо False, оскільки не всі квитки доступні для придбання
        if available_tickets:
            db.query(models.Ticket).filter(models.Ticket.ticket_id.in_(ticket_id)).update({models.Ticket.status: "sold"}, synchronize_session=False)

            # Зберігаємо зміни в базі даних
            db.commit()
            return True
        return False
    except Exception as e:
        # Якщо сталася помилка, відміняємо транзакцію та повертаємо False
        db.rollback()
        print(f"Error occurred: {e}")
        return False
    
def return_ticket(db: Session, ticket_id: int) -> bool:
    try:
        # Retrieve the ticket from the database
        ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
        
        if ticket:
            # Update the status of the ticket to "available"
            ticket.status = "available"
            ticket.user_id = -1
            
            # Commit changes to the database
            db.commit()
            return True
        else:
            return False
    except Exception as e:
        # Handle exceptions and rollback changes
        db.rollback()
        print(f"Error occurred: {e}")
        return False
    
def average_rate_for_event(reviews):
    total_rate = 0
    count = 0
    for review in reviews:
        total_rate += review["rate"]
        count += 1
        
    average_rate = total_rate / count if count > 0 else "null"
    return average_rate

def trim_dict_to_limit(input_dict, limit):
    res = {}
    for i in range(min(limit, len(input_dict))):
        res[list(input_dict.keys())[i]] = input_dict[list(input_dict.keys())[i]]
    
    return res