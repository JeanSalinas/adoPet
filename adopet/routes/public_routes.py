# adopet/routes/public_routes.py
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from adopet.database import get_mascotas_collection

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

# Obtener la colección de mascotas
mascotas_collection = get_mascotas_collection()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # pasamos session para que tus templates puedan usar session.get('is_admin')
    return templates.TemplateResponse(
        "index.html", {"request": request, "session": request.session}
    )


@router.get("/mascotas", response_class=HTMLResponse)
async def ver_mascotas(request: Request):
    mascotas = []
    # Leer todas las mascotas de la DB
    cursor = mascotas_collection.find({})
    async for doc in cursor:
        # convertir ObjectId a string y asegurar campos
        doc["id"] = str(doc.get("_id"))
        mascotas.append(doc)

    return templates.TemplateResponse(
        "mascotas.html",
        {"request": request, "mascotas": mascotas, "session": request.session},
    )
