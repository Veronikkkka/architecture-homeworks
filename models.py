from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric, CheckConstraint, Table
from sqlalchemy.orm import relationship

from database import Base

event_performer_association = Table(
    'event_performer_association',
    Base.metadata,
    Column('event_id', Integer, ForeignKey('event.event_id')),
    Column('performer_id', Integer, ForeignKey('performer.performer_id'))
)

class Event(Base):
    __tablename__ = "event"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    ticket_quantity = Column(Integer, nullable=False)
    performers = relationship("Performer", secondary=event_performer_association, back_populates="events")
    
    def __init__(self, name: str, date: str, time: str, venue: str, ticket_quantity: int, performers: list = None):
        self.name = name
        self.date = date
        self.time = time
        self.venue = venue
        self.ticket_quantity = ticket_quantity
        self.performers = []


class Performer(Base):
    __tablename__ = "performer"

    performer_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    events = relationship("Event", secondary=event_performer_association, back_populates="performers")
    def __init__(self, first_name: str, last_name: str, events: list = None):
        self.first_name = first_name
        self.last_name = last_name
        self.events = events or []
    
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("event.event_id"))
    type = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String(20), CheckConstraint("status IN ('sold', 'available', 'reserved')"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tickets")
    
    def __repr__(self):
        return f"{self.ticket_id}"
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    tickets = relationship("Ticket", back_populates="user")

class Description(Base):
    __tablename__ = "descriptions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
