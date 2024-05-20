from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date

import crud, models
import schemas2 as schemas
from database import SessionLocal, engine, collection, collection2
from models import Event
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.put("/events/{event_id}/", response_model=schemas.EventOut)
def update_event(event_id: int, event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.update_event(db=db, event_id=event_id, event=event)

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

@app.post("/events/", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event)


@app.get("/events/", response_model=list[schemas.EventOut])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events





@app.delete("/events/{event_id}/", response_model=schemas.EventOut)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return db_event

@app.post("/tickets/", response_model=schemas.TicketOut)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    event_id = ticket.event_id
    user_id = ticket.user_id
    return crud.create_ticket(db=db, ticket=ticket, event_id=event_id, user_id=user_id)

@app.get("/tickets/", response_model=list[schemas.TicketOut])
def get_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tickets(db, skip=skip, limit=limit)

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

@app.get("/events/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db=db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

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

@app.post('/descriptions/{event_id}')
async def create_description(event_id: int, description: schemas.DescriptionCreate, db: Session = Depends(get_db)):
    event = crud.get_event(db=db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    description_dict = dict(description)
    description_dict["event_id"] = event_id
    collection.insert_one(description_dict)

    return schemas.serializeList(collection.find())

@app.get("/reviews/{event_id}/{user_id}")
async def find_reviews(event_id: int, user_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db=db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tickets = crud.get_tickets_for_visitor(db, user_id)     
    was_on_event = False
    for ticket in tickets:
        if ticket.event_id == event_id:
            was_on_event = True
            break
    if was_on_event:  
        reviews = collection2.find({"event_id": event_id})
        average_rate = crud.average_rate_for_event(reviews)
        return {"reviews": schemas.serializeList(collection2.find({"event_id": event_id})), "average_rate": average_rate}
    else:
        raise HTTPException(status_code=404, detail="User was not on this event")
    


@app.post('/reviews/{event_id}/{user_id}/{rate}')
async def create_review(event_id: int, user_id: int, rate:int, review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    event = crud.get_event(db=db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tickets = crud.get_tickets_for_visitor(db, user_id)     
    was_on_event = False
    for ticket in tickets:
        if ticket.event_id == event_id:
            was_on_event = True
            break
    if was_on_event:
    
        if rate < 1 or rate > 10:
            raise HTTPException(status_code=404, detail="Rate is out of range")
        
        review_dict = dict(review)
        review_dict["event_id"] = event_id
        review_dict["user_id"] = user_id
        review_dict["rate"] = rate
        collection2.insert_one(review_dict)
        
        return schemas.serializeList(collection2.find())
    else:
        raise HTTPException(status_code=404, detail="User was not on this event")


# @app.get("/events/{limit}/{min_reviews}/")
# async def find_events_with_reviews(limit: int, min_reviews: int, min_average_rating: float = None, db: Session = Depends(get_db)):

#     events = crud.get_events(db=db)
#     result = []
#     for event in events:
#         if len(list(collection2.find({"event_id": event.event_id}))) >= min_reviews:
#             result.append((event, schemas.serializeList(collection2.find({"event_id": event.event_id}))))
#             # result.append()
    
#     if min_average_rating is not None:
#         res_events = []
#         for tuple in result:
#             event, reviews = tuple
#             if crud.average_rate_for_event(collection2.find({"event_id": event.event_id})) >= min_average_rating:            
#                 res_events.append((event, reviews))   
    
#         return res_events[:limit]
#     else:
#         return result[:limit]
    
from typing import Optional
@app.get("/events/search/")
async def find_events_with_reviews(limit: int, min_reviews: int, min_average_rating: Optional[float] = 0, db: Session = Depends(get_db)):
    events = crud.get_events(db=db)
    result = []
    for event in events:
        if len(list(collection2.find({"event_id": event.event_id}))) >= min_reviews:
            result.append((event, schemas.serializeList(collection2.find({"event_id": event.event_id}))))
            # result.append()
    
    if min_average_rating != 0:
        res_events = []
        for tuple in result:
            event, reviews = tuple
            if crud.average_rate_for_event(collection2.find({"event_id": event.event_id})) >= min_average_rating:            
                res_events.append((event, reviews))   
    
        return res_events[:limit]
    else:
        return result[:limit]