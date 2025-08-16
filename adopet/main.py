from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="AdoPet")

# Middleware para sesiones (necesario para request.session)
app.add_middleware(SessionMiddleware, secret_key="cambia_esta_clave_por_una_segura")

# Servir estáticos
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# importar rutas
from adopet.routes import public_routes, auth_routes, admin_routes

app.include_router(public_routes.router)
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
