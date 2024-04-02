from pydantic import BaseModel
from datetime import datetime


class EventCreate(BaseModel):
    name: str
    date: datetime
    time: str
    venue: str
    ticket_quantity: int
    performers: list
    
class PerformerOut(BaseModel):
    performer_id: int
    first_name: str
    last_name: str
    # events: list[EventOut]

    class Config:
        orm_mode = True

class EventOut(BaseModel):
    event_id: int
    name: str
    date: datetime
    time: str
    venue: str
    ticket_quantity: int
    performers: list[PerformerOut]

    class Config:
        orm_mode = True


class PerformerCreate(BaseModel):
    first_name: str
    last_name: str
    events: list[int] = []



        
class TicketCreate(BaseModel):
    event_id: int    
    type: str
    price: int
    status: str
    user_id: int

class TicketOut(BaseModel):
    ticket_id: int
    event_id: int    
    type: str
    price: int
    status: str
    user_id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    first_name: str
    last_name: str

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    tickets: list[TicketOut]

    class Config:
        orm_mode = True
        