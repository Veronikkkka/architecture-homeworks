# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# import os

# app = Flask(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# app.app_context().push()
# # db.init_app(app)
# db.create_all()

# class Event(db.Model):
#     event_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     time = db.Column(db.Time, nullable=False)
#     venue = db.Column(db.String(255), nullable=False)
#     ticket_quantity = db.Column(db.Integer, nullable=False)
    
#     def __repr__(self) -> str:
#         return f"{self.name}: {self.date}, {self.time}, {self.venue}, {self.ticket_quantity} "

# class Performer(db.Model):
#     performer_id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(255), nullable=False)
#     last_name = db.Column(db.String(255), nullable=False)
    
#     def __repr__(self) -> str:
#         return f"{self.first_name} {self.last_name}"

# class Ticket(db.Model):
#     ticket_id = db.Column(db.Integer, primary_key=True)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)
#     type = db.Column(db.String(50), nullable=False)
#     price = db.Column(db.Float, nullable=False)
#     status = db.Column(db.Enum('sold', 'available', 'reserved'), nullable=False)

# class User(db.Model):
#     user_id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(255), nullable=False)
#     last_name = db.Column(db.String(255), nullable=False)


# @app.route("/")
# def main():
#     return "Home"

# @app.route("/performers")
# def get_performers():
#     performers = Performer.query.all()
#     out = []
#     for i in performers:
#         data = {'name': i.first_name, "last name" : i.last_name}        
#         out.append(data)
        
#     return out

# if __name__ == '__main__':
#     app.app_context().push()
#     db.create_all()
#     app.run(debug=True)


# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from config import Config
# from sqlalchemy import text
# from sqlalchemy import inspect

# app = Flask(__name__)
# app.config.from_object(Config)
# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), index=True, unique=True)

#     def __repr__(self):
#         return '<User {}>'.format(self.username)

# @app.route('/test_db_connection')
# def test_db_connection():
#     print("HERE")
#     try:
#         db.session.execute(text('SELECT 1'))
#         inspector = inspect(db.engine)
#         table_names = inspector.get_table_names()
#         # print(table_names)
#         return f'Connection to the database successful {table_names}'
#     except Exception as e:
#         return f'Error connecting to the database: {str(e)}', 500
    
# if __name__ == "__main__":
#     app.run(debug=True)
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, CheckConstraint
from typing import List
from decimal import Decimal

app = FastAPI()


# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:password@mysql/bd"
SQLALCHEMY_DATABASE_URL = "sqlite:///./events.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/bd"
# SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/bd"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Base.metadata.create_all(bind=engine)

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)


class Event(Base):
    __tablename__ = "event"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    ticket_quantity = Column(Integer, nullable=False)
    
    
class EventCreate(BaseModel):
    name: str
    date: str
    time: str
    venue: str
    ticket_quantity: int


class EventOut(BaseModel):
    event_id: int
    name: str
    date: str
    time: str
    venue: str
    ticket_quantity: int

    class Config:
        orm_mode = True

class Performer(Base):
    __tablename__ = "performer"

    performer_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)


class PerformerCreate(BaseModel):
    first_name: str
    last_name: str


class PerformerOut(BaseModel):
    performer_id: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    type = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), CheckConstraint("status IN ('sold', 'available', 'reserved')"), nullable=False)

class TicketCreate(BaseModel):
    event_id: int
    type: str
    price: Decimal
    status: str

class TicketOut(BaseModel):
    ticket_id: int
    event_id: int
    type: str
    price: Decimal
    status: str

    class Config:
        orm_mode = True



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/events/", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/", response_model=List[EventOut])
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events

@app.put("/events/{event_id}/", response_model=EventOut)
def update_event(event_id: int, event_data: EventCreate, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    for attr, value in event_data.dict().items():
        setattr(db_event, attr, value)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/events/{event_id}/", response_model=EventOut)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.event_id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return db_event


@app.post("/performers/", response_model=PerformerOut)
def create_performer(performer: PerformerCreate, db: Session = Depends(get_db)):
    db_performer = Performer(**performer.dict())
    db.add(db_performer)
    db.commit()
    db.refresh(db_performer)
    return db_performer

@app.get("/performers/", response_model=List[PerformerOut])
def get_performers(db: Session = Depends(get_db)):
    performers = db.query(Performer).all()
    return performers

@app.put("/performers/{performer_id}/", response_model=PerformerOut)
def update_performer(performer_id: int, performer_data: PerformerCreate, db: Session = Depends(get_db)):
    db_performer = db.query(Performer).filter(Performer.performer_id == performer_id).first()
    if db_performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    for attr, value in performer_data.dict().items():
        setattr(db_performer, attr, value)
    db.commit()
    db.refresh(db_performer)
    return db_performer

@app.delete("/performers/{performer_id}/", response_model=PerformerOut)
def delete_performer(performer_id: int, db: Session = Depends(get_db)):
    db_performer = db.query(Performer).filter(Performer.performer_id == performer_id).first()
    if db_performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    db.delete(db_performer)
    db.commit()
    return db_performer


@app.post("/tickets/", response_model=TicketOut)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.get("/tickets/", response_model=List[TicketOut])
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return tickets

@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.put("/tickets/{ticket_id}/", response_model=TicketOut)
def update_ticket(ticket_id: int, ticket_data: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for attr, value in ticket_data.dict().items():
        setattr(db_ticket, attr, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.delete("/tickets/{ticket_id}/", response_model=TicketOut)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    db_ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(db_ticket)
    db.commit()
    return db_ticket


@app.get("/test_db_connection")
def test_db_connection():
    try:
        with engine.connect() as connection:
            # result = connection.execute(text("SELECT 1"))
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            result = connection.execute(text("PRAGMA database_list;"))
            row = result.fetchone()
            db_name = row[2] if row else None
            return {"message": db_name, "tables": table_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to the database: {str(e)}")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
