from adopet.database import get_database
from passlib.context import CryptContext

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Obtener colección de administradores
db = get_database()
admins_collection = db["admins"] if db is not None else None


async def verify_user(username: str, password: str) -> bool:
    """
    Verifica credenciales de un usuario admin contra la base de datos
    """
    if admins_collection is None:
        return False  # No hay conexión a la DB

    admin = await admins_collection.find_one({"username": username})
    if not admin:
        return False

    hashed_password = admin.get("password")
    if not hashed_password:
        return False

    return pwd_context.verify(password, hashed_password)


async def create_admin(username: str, password: str, telefono: str):
    """
    Crea un nuevo admin en la base de datos con contraseña hasheada
    """
    if admins_collection is None:
        return None  # No hay conexión a la DB

    hashed_password = pwd_context.hash(password)
    admin_doc = {
        "username": username,
        "password": hashed_password,
        "telefono": telefono
    }
    result = await admins_collection.insert_one(admin_doc)
    return result.inserted_id
