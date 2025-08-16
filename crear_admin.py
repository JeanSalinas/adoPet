import asyncio
from adopet.services.auth_service import create_admin

async def main():
    username = "admin"
    password = "123456"
    telefono = "3001234567"
    admin_id = await create_admin(username, password, telefono)
    print("Admin creado con id:", admin_id)

asyncio.run(main())