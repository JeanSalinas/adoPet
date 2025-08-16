# adopet/routes/admin_routes.py
from pathlib import Path
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from uuid import uuid4
from bson import ObjectId

from adopet.database import get_mascotas_collection, get_database
from adopet.services.auth_service import pwd_context

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()
UPLOAD_DIR = BASE_DIR / "static" / "img"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Base de datos
db = get_database()
admins_collection = db["admins"]


# -------------------------------
# DASHBOARD ADMIN
# -------------------------------
@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "admin_dashboard.html", {"request": request, "session": request.session}
    )


# -------------------------------
# LISTADO DE MASCOTAS
# -------------------------------
@router.get("/admin/mascotas", response_class=HTMLResponse)
async def admin_mascotas(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")
    mascotas_collection = get_mascotas_collection()
    mascotas = await mascotas_collection.find().to_list(100)
    return templates.TemplateResponse(
        "admin_mascotas.html",
        {"request": request, "mascotas": mascotas, "session": request.session},
    )


# -------------------------------
# CAMBIAR ESTADO
# -------------------------------
@router.post("/admin/cambiar_estado/{pet_id}")
async def cambiar_estado(request: Request, pet_id: str, estado: str = Form(...)):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")
    mascotas_collection = get_mascotas_collection()
    await mascotas_collection.update_one(
        {"_id": ObjectId(pet_id)},
        {
            "$set": {
                "estado": estado,
                "contacto": "3001234567" if estado == "Disponible" else "",
            }
        },
    )
    return RedirectResponse(
        url="/admin/mascotas", status_code=status.HTTP_303_SEE_OTHER
    )


# -------------------------------
# REGISTRO DE MASCOTAS
# -------------------------------
@router.get("/admin/registro", response_class=HTMLResponse)
async def registro_get(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "admin_registro.html", {"request": request, "session": request.session}
    )


@router.post("/admin/registro")
async def registro_post(
    request: Request,
    nombre: str = Form(...),
    especie: str = Form(...),
    raza: str = Form(...),
    tamaño: str = Form(...),
    vacunacion: str = Form(...),
    estado: str = Form(...),
    edad: str = Form(...),
    foto: UploadFile | None = File(None),
):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")

    mascotas_collection = get_mascotas_collection()

    foto_url = "/static/img/default_pet.png"
    if foto and foto.filename:
        ext = Path(foto.filename).suffix
        filename = f"{uuid4().hex}{ext}"
        dest = UPLOAD_DIR / filename
        with open(dest, "wb") as f:
            content = await foto.read()
            f.write(content)
        foto_url = f"/static/img/{filename}"

    nuevo = {
        "nombre": nombre,
        "especie": especie,
        "tamaño": tamaño,
        "raza": raza,
        "edad": edad,
        "vacunacion": vacunacion,
        "estado": estado,
        "foto": foto_url,
        "contacto": "3001234567" if estado == "Disponible" else "",
    }

    await mascotas_collection.insert_one(nuevo)
    return RedirectResponse(
        url="/admin/mascotas", status_code=status.HTTP_303_SEE_OTHER
    )


# -------------------------------
# EDITAR MASCOTA
# -------------------------------
@router.get("/admin/editar_mascota/{pet_id}", response_class=HTMLResponse)
async def editar_mascota_get(request: Request, pet_id: str):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")

    mascotas_collection = get_mascotas_collection()
    try:
        obj_id = ObjectId(pet_id)
    except:
        return RedirectResponse(url="/admin/mascotas")

    mascota = await mascotas_collection.find_one({"_id": obj_id})
    if not mascota:
        return RedirectResponse(url="/admin/mascotas")

    # Convertir _id a string para el HTML
    mascota["_id"] = str(mascota["_id"])

    # Tomar mensaje de sesión si existe
    update_msg = request.session.pop("update_msg", None)

    return templates.TemplateResponse(
        "editar_mascota.html",
        {
            "request": request,
            "mascota": mascota,
            "session": request.session,
            "update_msg": update_msg,
        },
    )


# POST: actualizar mascota
@router.post("/admin/editar_mascota/{pet_id}")
async def editar_mascota_post(
    request: Request,
    pet_id: str,
    nombre: str = Form(...),
    especie: str = Form(...),
    raza: str = Form(...),
    tamaño: str = Form(...),
    vacunacion: str = Form(...),
    estado: str = Form(...),
    edad: str = Form(...),
    foto: UploadFile | None = File(None),
):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")

    mascotas_collection = get_mascotas_collection()

    try:
        obj_id = ObjectId(pet_id)
    except:
        request.session["update_msg"] = "ID de mascota inválido"
        return RedirectResponse(url=f"/admin/editar_mascota/{pet_id}")

    update_data = {
        "nombre": nombre,
        "especie": especie,
        "raza": raza,
        "tamaño": tamaño,
        "vacunacion": vacunacion,
        "estado": estado,
        "edad": edad,
        "contacto": "3001234567" if estado == "Disponible" else "",
    }

    # Procesar foto si se sube
    if foto and foto.filename:
        ext = Path(foto.filename).suffix
        filename = f"{uuid4().hex}{ext}"
        dest = UPLOAD_DIR / filename
        try:
            with open(dest, "wb") as f:
                f.write(await foto.read())
            update_data["foto"] = f"/static/img/{filename}"
        except Exception as e:
            print("Error al guardar foto:", e)

    result = await mascotas_collection.update_one(
        {"_id": obj_id}, {"$set": update_data}
    )

    if result.modified_count == 0:
        request.session["update_msg"] = "No se realizaron cambios"
    else:
        request.session["update_msg"] = "Mascota actualizada correctamente"

    # Redirigir al mismo formulario para mostrar mensaje
    return RedirectResponse(
        url=f"/admin/mascotas", status_code=status.HTTP_303_SEE_OTHER
    )


# -------------------------------
# EDITAR ADMIN
# -------------------------------
@router.get("/admin/editar_admin", response_class=HTMLResponse)
async def editar_admin_get(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")

    admin_data = await admins_collection.find_one({"username": "admin"})
    if not admin_data:
        admin_data = {"username": "admin", "telefono": "3001234567"}

    return templates.TemplateResponse(
        "editar_admin.html",
        {
            "request": request,
            "admin": admin_data,
            "session": request.session,
            "error_msg": "",
        },
    )


@router.post("/admin/editar_admin")
async def editar_admin_post(
    request: Request,
    password: str = Form(""),  # Nueva contraseña opcional
    confirm_password: str = Form(""),  # Confirmación opcional
    telefono: str = Form(...),
):
    if not request.session.get("is_admin"):
        return RedirectResponse(url="/login")

    # Si se ingresó contraseña, validar que coincida
    if password or confirm_password:
        if password != confirm_password:
            admin_data = await admins_collection.find_one({"username": "admin"})
            return templates.TemplateResponse(
                "editar_admin.html",
                {
                    "request": request,
                    "admin": admin_data,
                    "session": request.session,
                    "error_msg": "Las contraseñas no coinciden",
                },
            )
        hashed_password = pwd_context.hash(password)
    else:
        hashed_password = None

    # Actualizar datos
    update_data = {"telefono": telefono}
    if hashed_password:
        update_data["password"] = hashed_password

    await admins_collection.update_one({"username": "admin"}, {"$set": update_data})

    request.session["admin_data"] = {"username": "admin", "telefono": telefono}

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
