# adopet/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "adopet_db"

# Función para obtener la base de datos
def get_database():
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        return db
    except ServerSelectionTimeoutError as e:
        print("No se pudo conectar a MongoDB:", e)
        return None

# Función para obtener la colección de mascotas
def get_mascotas_collection():
    db = get_database()
    if db is not None:
        return db["mascotas"]
    return None

# Función para obtener la colección de administradores
def get_admins_collection():
    db = get_database()
    if db is not None:
        return db["admins"]
    return None
