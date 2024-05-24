from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Time, DECIMAL, Enum, ForeignKey
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, CheckConstraint
# Параметри підключення до бази даних
# db_url = "mysql+mysqlconnector://root:password@mysql/bd"
# db_url = 'sqlite:///./events.db'  
# # db_url = "postgresql://username:password@localhost/bd"

# # db_url = 'sqlite:///./events.db'  
# # Створення об'єкта для роботи з базою даних
# engine = create_engine(db_url)

# Об'єкт для визначення таблиць і стовпців
# metadata = MetaData()


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./events.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# Таблиця Event
# event_table = Table(
#     'Event', metadata,
#     Column('event_id', Integer, primary_key=True, autoincrement=True),
#     Column('name', String(255), nullable=False),
#     Column('date', Date, nullable=False),
#     Column('time', Time, nullable=False),
#     Column('venue', String(255), nullable=False),
#     Column('ticket_quantity', Integer, nullable=False)
# )

# # Таблиця Performer
# performer_table = Table(
#     'Performer', metadata,
#     Column('performer_id', Integer, primary_key=True, autoincrement=True),
#     Column('first_name', String(255), nullable=False),
#     Column('last_name', String(255), nullable=False)
# )

# # Таблиця Ticket
# ticket_table = Table(
#     'Ticket', metadata,
#     Column('ticket_id', Integer, primary_key=True, autoincrement=True),
#     Column('event_id', Integer, ForeignKey('Event.event_id')),
#     Column('type', String(50), nullable=False),
#     Column('price', DECIMAL(10, 2), nullable=False),
#     Column('status', Enum('sold', 'available', 'reserved'), nullable=False)
# )

# # Таблиця User
# user_table = Table(
#     'User', metadata,
#     Column('user_id', Integer, primary_key=True, autoincrement=True),
#     Column('first_name', String(255), nullable=False),
#     Column('last_name', String(255), nullable=False)
# )

# # Створення таблиць у базі даних
# metadata.create_all(engine)
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    type = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), CheckConstraint("status IN ('sold', 'available', 'reserved')"), nullable=False)
    
class Performer(Base):
    __tablename__ = "performer"

    performer_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
class Event(Base):
    __tablename__ = "event"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    ticket_quantity = Column(Integer, nullable=False)
    