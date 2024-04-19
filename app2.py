from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy import create_engine, text, inspect
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy.exc import IntegrityError
# from pydantic import BaseModel
# from sqlalchemy import Column, Integer, String
# from typing import List


app = FastAPI()

@app.get("/")
def hello():
    return "Hello world"

# SQLALCHEMY_DATABASE_URL = "sqlite:///./events.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)


# class Event(Base):
#     __tablename__ = "event"

#     event_id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     date = Column(String, nullable=False)
#     time = Column(String, nullable=False)
#     venue = Column(String, nullable=False)
#     ticket_quantity = Column(Integer, nullable=False)
    
    
# class EventCreate(BaseModel):
#     name: str
#     date: str
#     time: str
#     venue: str
#     ticket_quantity: int


# class EventOut(BaseModel):
#     event_id: int
#     name: str
#     date: str
#     time: str
#     venue: str
#     ticket_quantity: int

#     class Config:
#         orm_mode = True

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @app.post("/events/", response_model=EventOut)
# def create_event(event: EventCreate, db: Session = Depends(get_db)):
#     db_event = Event(**event.dict())
#     db.add(db_event)
#     db.commit()
#     db.refresh(db_event)
#     return db_event

# @app.get("/events/", response_model=List[EventOut])
# def get_events(db: Session = Depends(get_db)):
#     events = db.query(Event).all()
#     return events

# @app.put("/events/{event_id}/", response_model=EventOut)
# def update_event(event_id: int, event_data: EventCreate, db: Session = Depends(get_db)):
#     db_event = db.query(Event).filter(Event.event_id == event_id).first()
#     if db_event is None:
#         raise HTTPException(status_code=404, detail="Event not found")
#     for attr, value in event_data.dict().items():
#         setattr(db_event, attr, value)
#     db.commit()
#     db.refresh(db_event)
#     return db_event

# @app.delete("/events/{event_id}/", response_model=EventOut)
# def delete_event(event_id: int, db: Session = Depends(get_db)):
#     db_event = db.query(Event).filter(Event.event_id == event_id).first()
#     if db_event is None:
#         raise HTTPException(status_code=404, detail="Event not found")
#     db.delete(db_event)
#     db.commit()
#     return db_event

# @app.get("/test_db_connection")
# def test_db_connection():
#     try:
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             inspector = inspect(engine)
#             table_names = inspector.get_table_names()
#             return {"message": "Connection to the database successful", "tables": table_names}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error connecting to the database: {str(e)}")

# if __name__ == "__main__":
#     Base.metadata.create_all(bind=engine)