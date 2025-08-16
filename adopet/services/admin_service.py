# adopet/services/admin_service.py
from adopet.database import get_admins_collection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_admin(username: str):
    admins_col = get_admins_collection()
    if not admins_col:
        return None
    return await admins_col.find_one({"username": username})

async def update_admin(username: str, password: str, telefono: str):
    admins_col = get_admins_collection()
    if not admins_col:
        return False
    hashed_password = pwd_context.hash(password)
    result = await admins_col.update_one(
        {"username": username},
        {"$set": {"password": hashed_password, "telefono": telefono}}
    )
    return result.modified_count > 0

async def verify_admin(username: str, password: str) -> bool:
    admin = await get_admin(username)
    if not admin:
        return False
    return pwd_context.verify(password, admin["password"])
