from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date

import crud, models
import schemas2 as schemas
from database import SessionLocal, engine, collection, collection2
from models import Event
import json
from redis_cache import RedisCache

import limiter
import secrets
import asyncio

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
limiter_ = limiter.RateLimiter()
api_keys = []


def get_api_key():
    return secrets.token_urlsafe(24)

@app.get("/apikey")
async def generate_api_key():
    api_key = get_api_key()
    api_keys.append(api_key)
    return {"api_key": api_key}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/descriptions/{event_id}')
async def get_description(event_id: int):
    # Спробуємо отримати опис події з кешу
    description_key = f"des_{event_id}"
    cached_description = redis_cache.get(description_key)
    if cached_description:
        # Якщо опис знайдено у кеші, повертаємо його
        return cached_description
    
    # Якщо опис відсутній у кеші, отримуємо його з бази даних
    db_description = collection.find({"event_id": event_id})
    if db_description is None:
        raise HTTPException(status_code=404, detail="Description not found")
    
    
    # Зберігаємо отриманий опис у кеші
    redis_cache.set(description_key, schemas.serializeList(db_description))
    
    return redis_cache.get(description_key)

@app.get("/events/availability", response_model=list[schemas.EventOut])
def get_events_availability(db: Session = Depends(get_db)):
    events = crud.get_events_by_date(db=db)
    events_sold = crud.get_events_with_sold_out_tickets(db=db)
    all_events = events + events_sold
    return all_events

@app.put("/performers/{performer_id}/", response_model=schemas.PerformerOut)
def update_performer(performer_id: int, performer: schemas.PerformerCreate, db: Session = Depends(get_db)):
    # db_performer = crud.get_performer(db, performer_id)
    # if db_performer is None:
    #     raise HTTPException(status_code=404, detail="Performer not found")
    return crud.update_performer(db=db, performer_id=performer_id, performer=performer)

# @app.put("/events/{event_id}/", response_model=schemas.EventOut)
# def update_event(event_id: int, event: schemas.EventCreate, db: Session = Depends(get_db)):
#     return crud.update_event(db=db, event_id=event_id, event=event)

@app.get("/events/{event_id}/reserved-users", response_model=list[schemas.UserOut])
def get_reserved_users_for_event(event_id: int, db: Session = Depends(get_db)):
    reserved_users = crud.get_users_reserved_tickets_for_event(db, event_id)
    return reserved_users

@app.get("/tickets/{user_id}/", response_model=list[schemas.TicketOut])
def get_tickets_for_visitor(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    tickets = crud.get_tickets_for_visitor(db, user_id)
    return tickets

# @app.post("/events/", response_model=schemas.EventOut)
# def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
#     return crud.create_event(db=db, event=event)


@app.get("/events/", response_model=list[schemas.EventOut])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events





# @app.delete("/events/{event_id}/", response_model=schemas.EventOut)
# def delete_event(event_id: int, db: Session = Depends(get_db)):
#     db_event = db.query(Event).filter(Event.event_id == event_id).first()
#     if db_event is None:
#         raise HTTPException(status_code=404, detail="Event not found")
#     db.delete(db_event)
#     db.commit()
#     return db_event

# @app.post("/tickets/", response_model=schemas.TicketOut)
# def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
#     event_id = ticket.event_id
#     user_id = ticket.user_id
#     return crud.create_ticket(db=db, ticket=ticket, event_id=event_id, user_id=user_id)



def update_rate_limiter():
    limiter_.update_bucket()

async def periodic_update_rate_limiter(background_tasks: BackgroundTasks):
    while True:
        background_tasks.add_task(update_rate_limiter)
        await asyncio.sleep(1)  # Update rate limiter every second


@app.get("/tickets")
async def read_tickets(api_key: str, db: Session = Depends(get_db)):
    if api_key not in api_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    if not limiter_.allow_request(api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # return limiter_.tokens
    return crud.get_tickets(db)
    
# , response_model=schemas.TicketOut
@app.post("/tickets")
def create_ticket(api_key:str, ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    event_id = ticket.event_id
    user_id = ticket.user_id
    if api_key not in api_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    if not limiter_.allow_request(api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # return limiter_.tokens
    return crud.create_ticket(db=db, ticket=ticket, event_id=event_id, user_id=user_id)


# @app.get("/tickets/", response_model=list[schemas.TicketOut])
# def get_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.get_tickets(db, skip=skip, limit=limit)

@app.put("/tickets/{ticket_id}/", response_model=schemas.TicketOut)
def update_ticket(ticket_id: int, ticket_data: schemas.TicketCreate, db: Session = Depends(get_db)):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket attributes with new data
    for attr, value in ticket_data.dict().items():
        setattr(db_ticket, attr, value)
    
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.delete("/tickets/{ticket_id}/", response_model=schemas.TicketOut)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(db_ticket)
    db.commit()
    return db_ticket

@app.post("/performers/", response_model=schemas.PerformerOut)
def create_performer(performer: schemas.PerformerCreate, db: Session = Depends(get_db)):
    return crud.create_performer(db=db, performer=performer)

@app.get("/performers/", response_model=list[schemas.PerformerOut])
def get_performers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    performers = crud.get_performers(db, skip=skip, limit=limit)
    return performers



@app.delete("/performers/{performer_id}/", response_model=schemas.PerformerOut)
def delete_performer(performer_id: int, db: Session = Depends(get_db)):
    db_performer = db.query(models.Performer).filter(models.Performer.performer_id == performer_id).first()
    if db_performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    db.delete(db_performer)
    db.commit()
    return db_performer

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    for user in users:
        user.tickets = crud.get_user_tickets(db, user.id)
    return users

@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserCreate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/{user_id}", response_model=schemas.UserOut)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted_user = crud.delete_user(db, user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user
# @app.get("/users/", response_model=list[schemas.UserOut])
# def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users

@app.post("/events/{event_id}/performers/{performer_id}", response_model=schemas.EventOut)
def add_performer_to_event(event_id: int, performer_id: int, db: Session = Depends(get_db)):
    # Перевіряємо, чи існує подія з вказаним event_id
    db_event = crud.get_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Перевіряємо, чи існує виконавець з вказаним performer_id
    db_performer = crud.get_performer(db, performer_id)
    if db_performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    
    # Додаємо виконавця до списку виконавців події
    db_event = crud.add_performer_to_event(db, event_id, performer_id)
    
    # Повертаємо оновлену інформацію про подію
    return db_event

@app.get("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db=db, ticket_id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

# @app.get("/events/{event_id}", response_model=schemas.EventOut)
# def get_event(event_id: int, db: Session = Depends(get_db)):
#     event = crud.get_event(db=db, event_id=event_id)
#     if event is None:
#         raise HTTPException(status_code=404, detail="Event not found")
#     return event



@app.get("/performers/{performer_id}", response_model=schemas.PerformerOut)
def get_performer(performer_id: int, db: Session = Depends(get_db)):
    performer = crud.get_performer(db=db, performer_id=performer_id)
    if performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    return performer

# @app.put("/tickets/reserve/{event_id}", response_model=schemas.TicketOut)
# def reserve_ticket(event_id: int, user_id: int = -1, duration: int = 15, db: Session = Depends(SessionLocal)):
    
#     # Check if the event exists
#     event = crud.get_event(db, event_id)
#     if not event:
#         raise HTTPException(status_code=404, detail="Event not found")

#     # Check if the user exists
#     user = crud.get_user(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Reserve the ticket
#     ticket = crud.reserve_ticket(db, event_id, user_id, duration)
#     if not ticket:
#         raise HTTPException(status_code=400, detail="Ticket cannot be reserved")

#     return ticket

@app.put("/tickets/reserve/{ticket_id}/", response_model=schemas.TicketOut)
def reserve_ticket(ticket_id: int,  user_id: int = -1, db: Session = Depends(get_db)):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    
    # Check if the user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Reserve the ticket
    db_ticket = crud.reserve_ticket(db, ticket_id, user_id)
    
    return db_ticket


@app.get("/tickets/{event_id}/date/")
def get_tickets_for_event_date(event_id: int, date: datetime, db: Session = Depends(get_db)):
    tickets = crud.get_tickets_for_event(db=db, event_id=event_id, date=date)
    return tickets

@app.get("/performers/events/", response_model=list[schemas.PerformerOut])
def get_all_performers(db: Session = Depends(get_db)):
    performers = crud.get_performers_with_events(db)
    return performers

@app.post("/purchase-tickets/{visitor_id}", response_model=list[schemas.TicketOut])
def purchase_tickets(event_id: int, user_id: int, ticket_id: list[int], db: Session = Depends(get_db)):
    success = crud.purchase_tickets(db, user_id, event_id, ticket_id)
    if success:
        return crud.get_tickets(db)
    else:
        raise HTTPException(status_code=404, detail="Failed to purchase tickets")
    
@app.put("/return-ticket/{ticket_id}")
def return_ticket(ticket_id: int, db: Session = Depends(get_db)):
    success = crud.return_ticket(db, ticket_id)
    if success:
        return {"message": "Ticket returned successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed to return ticket")
    
# @app.post("/descriptions/")
# async def create_description(description: schemas.DescriptionCreate):
#     description_dict = description.dict()
#     result = collection.insert_one(description_dict)
#     return {"id": str(result.inserted_id)}


# @app.get("/descriptions/", response_model=list[schemas.DescriptionOut])
# async def get_descriptions():
#     descriptions = collection.find()
#     descriptions_list = []
#     for desc in descriptions:
#         desc['_id'] = str(desc['_id'])  # Перетворення ObjectId на рядок
#         descriptions_list.append(schemas.DescriptionOut(**desc))  # Створення об'єкта DescriptionOut з MongoDB об'єкта
#     return descriptions_list

@app.get("/descriptions/")
async def get_descriptions():
    return schemas.serializeList(collection.find())

# @app.post('/descriptions/{event_id}')
# async def create_description(event_id: int, description: schemas.DescriptionCreate, db: Session = Depends(get_db)):
#     event = crud.get_event(db=db, event_id=event_id)
#     if event is None:
#         raise HTTPException(status_code=404, detail="Event not found")
    
#     description_dict = dict(description)
#     description_dict["event_id"] = event_id
#     collection.insert_one(description_dict)

#     return schemas.serializeList(collection.find())

# @app.get("/reviews/{event_id}")
# async def find_reviews(event_id: int, db: Session = Depends(get_db)):
#     event = crud.get_event(db=db, event_id=event_id)
#     if event is None:
#         raise HTTPException(status_code=404, detail="Event not found")
#     else:        
#         reviews = collection2.find({"event_id": event_id})
#         average_rate = crud.average_rate_for_event(reviews)
#         return {"reviews": schemas.serializeList(collection2.find({"event_id": event_id})), "average_rate": average_rate}
    


# @app.post('/reviews/{event_id}/{user_id}/{rate}')
# async def create_review(event_id: int, user_id: int, rate:int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
#     event = crud.get_event(db=db, event_id=event_id)
#     if event is None:
#         raise HTTPException(status_code=404, detail="Event not found")
    
#     user = crud.get_user(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     if rate < 1 or rate > 10:
#         raise HTTPException(status_code=404, detail="Rate is out of range")
    
#     review_dict = dict(review)
#     review_dict["event_id"] = event_id
#     review_dict["user_id"] = user_id
#     review_dict["rate"] = rate
#     collection2.insert_one(review_dict)
    
#     return schemas.serializeList(collection2.find())


@app.get("/events/{limit}/{min_reviews}/")
async def find_events_with_reviews(limit: int, min_reviews: int, min_average_rating: float = None, db: Session = Depends(get_db)):

    events = crud.get_events(db=db)
    result = []
    for event in events:
        if len(list(collection2.find({"event_id": event.event_id}))) >= min_reviews:
            result.append((event, schemas.serializeList(collection2.find({"event_id": event.event_id}))))
            # result.append()
    
    if min_average_rating is not None:
        res_events = []
        for tuple in result:
            event, reviews = tuple
            if crud.average_rate_for_event(collection2.find({"event_id": event.event_id})) >= min_average_rating:            
                res_events.append((event, reviews))   
    
        return res_events[:limit]
    else:
        return result[:limit]
    
    
redis_cache = RedisCache()

@app.get("/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    cached_event = redis_cache.get(event_id)
    if cached_event:
        return cached_event
        # return "Here"

    event = crud.get_event(db=db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    redis_cache.set(event_id, event)

    return event


@app.post("/events/", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    new_event = crud.create_event(db=db, event=event)
    redis_cache.set(new_event.event_id, new_event)
    return new_event

@app.put("/events/{event_id}/", response_model=schemas.EventOut)
def update_event(event_id: int, event: schemas.EventCreate, db: Session = Depends(get_db)):    
    updated_event = crud.update_event(db=db, event_id=event_id, event=event)
    redis_cache.set(event_id, updated_event)
    return updated_event

@app.delete("/events/{event_id}/", response_model=schemas.EventOut)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    redis_cache.delete(event_id)
    return db_event

@app.post('/descriptions/{event_id}')
async def create_description(event_id: int, description: schemas.DescriptionCreate, db: Session = Depends(get_db)):
    cached_event = redis_cache.get(event_id)
    if cached_event:
        event = cached_event
    else:
        # Якщо подія відсутня у кеші, отримуємо її з бази даних
        event = crud.get_event(db=db, event_id=event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        # Зберігаємо подію у кеші
        redis_cache.set(event_id, event)

    existing_description = collection.find_one({"event_id": event_id})
    if existing_description:
        raise HTTPException(status_code=400, detail="Description for this event already exists")

    # Додаємо опис події до бази даних
    description_dict = dict(description)
    description_dict["event_id"] = event_id
    collection.insert_one(description_dict)

    redis_cache.set(f"des_{event_id}", description_dict)

    return schemas.serializeList(collection.find())



@app.put('/descriptions/{event_id}')
async def update_description(event_id: int, description: schemas.DescriptionCreate):
    # # Спробуємо отримати подію з кешу
    # cached_event = redis_cache.get(event_id)
    # if cached_event:
    #     event = cached_event
    # else:
    #     # Якщо подія відсутня у кеші, отримуємо її з бази даних
    #     event = crud.get_event(db=db, event_id=event_id)
    #     if event is None:
    #         raise HTTPException(status_code=404, detail="Event not found")

    #     # Зберігаємо подію у кеші
    #     redis_cache.set(event_id, event)

    # # Оновлюємо опис події у базі даних
    # description_dict = dict(description)
    # description_dict["event_id"] = event_id
    # collection.update_one({"event_id": event_id}, {"$set": description_dict}, upsert=True)

    # # Оновлюємо опис події у кеші
    # redis_cache.set(f"des_{event_id}", event)

    # return {"message": "Description updated successfully"}
    description_key = f"des_{event_id}"
    cached_description = redis_cache.get(description_key)
    if cached_description:
        desc = cached_description
    else:
        desc = collection.find({"event_id": event_id})
        if desc is None:
            raise HTTPException(status_code=404, detail="Description not found")
    
    description_dict = dict(description)
    description_dict["event_id"] = event_id
    collection.update_one({"event_id": event_id}, {"$set": description_dict}, upsert=True)
    redis_cache.set(description_key, schemas.serializeList(collection.find({'event_id': event_id})))

    return redis_cache.get(description_key)
    

@app.delete('/descriptions/{event_id}')
async def delete_description(event_id: int):
    description_key = f"des_{event_id}"
    cached_description = redis_cache.get(description_key)
    if cached_description:
        redis_cache.delete(description_key)
    
    
    deleted_description = collection.find_one_and_delete({"event_id": event_id})
    if deleted_description is None:
        raise HTTPException(status_code=404, detail="Description not found")
    
    return {"Successfuly deleted"}

@app.get("/reviews/{event_id}")
async def find_reviews(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db=db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    else:
        key = f"r_{event_id}"
        cached = redis_cache.get(key)
        if cached:
            return cached
        
        reviews = collection2.find({"event_id": event_id})
        if reviews is None:
            raise HTTPException(status_code=404, detail="Description not found")
        
        
        # reviews = collection2.find({"event_id": event_id})
        average_rate = crud.average_rate_for_event(reviews)
        result = {"reviews": schemas.serializeList(collection2.find({"event_id": event_id})), "average_rate": average_rate}
        redis_cache.set(key, result)
        return redis_cache.get(key)
    


@app.post('/reviews/{event_id}/{user_id}/{rate}')
async def create_review(event_id: int, user_id: int, rate:int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    cached_event = redis_cache.get(event_id)
    if cached_event:
        event = cached_event
    else:
        # Якщо подія відсутня у кеші, отримуємо її з бази даних
        event = crud.get_event(db=db, event_id=event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        # Зберігаємо подію у кеші
        redis_cache.set(event_id, event)
    
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if rate < 1 or rate > 10:
        raise HTTPException(status_code=404, detail="Rate is out of range")
    
    review_dict = dict(review)
    review_dict["event_id"] = event_id
    review_dict["user_id"] = user_id
    review_dict["rate"] = rate
    collection2.insert_one(review_dict)
    

    redis_cache.set(f"r_{event_id}", schemas.serializeList(collection2.find({'event_id': event_id})))
    return redis_cache.get(f"r_{event_id}")

@app.delete('/reviews/{event_id}')
async def delete_review(event_id: int):
    key = f"r_{event_id}"
    cached_review = redis_cache.get(key)
    if cached_review:
        redis_cache.delete(key)
    
    
    deleted_review = collection2.find_one_and_delete({"event_id": event_id})
    if deleted_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {"Successfuly deleted"}


@app.get("/events_cached/{event_id}/")
async def event_with_description_and_reviews(event_id: int, db: Session = Depends(get_db)):

    event = crud.get_event(db=db, event_id=event_id)
    result = []
    key = f"e_{event_id}"
    cached_event = redis_cache.get(key)
    if cached_event:
        return cached_event
    else:
        reviews = await find_reviews(event_id, db)
        description = await get_description(event_id)
        # reviews = schemas.serializeList(collection2.find({"event_id": event_id}))
        cached_data = {"event": event, "description": description or [], "reviews": reviews or []}
        redis_cache.set(key, cached_data)
        
    
    return redis_cache.get(key)
    