from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from pymongo import MongoClient

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# client = MongoClient(f"mongodb://mongodb:27017/")
# db = client.events_database
# collection = db.get_collection("description")
# collection2 = db.get_collection("review")
# collection = db['events']
# collection.insert_one({"1":"1"})
# collections = db.inventory.find()
# if collections:
#     print("HEREE"*80)
# print("No"*80)