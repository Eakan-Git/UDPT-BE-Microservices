from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")

if not all([db_user, db_password, db_host]):
    raise ValueError("Environment variables DB_USER, DB_PASSWORD, and DB_HOST must be set.")

MONGO_URI = f"mongodb+srv://{db_user}:{db_password}@{db_host}/"
DB_NAME = os.getenv("DB_NAME")
client = AsyncIOMotorClient(MONGO_URI)
engine = AIOEngine(client=client, database=DB_NAME)