# adopet/routes/auth_routes.py
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from adopet.services.auth_service import verify_user  # <-- usamos la función con DB

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # mostramos el login, sin error
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None, "session": request.session}
    )


@router.post("/login")
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Verifica credenciales y crea sesión (request.session['is_admin'] = True)
    usando la base de datos
    """
    is_valid = await verify_user(username, password)
    if is_valid:
        # crear sesión
        request.session["is_admin"] = True
        # redirigir al panel admin
        response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
        return response

    # credenciales inválidas -> mostrar error en la misma plantilla
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Usuario o contraseña incorrectos", "session": request.session},
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@router.get("/logout")
async def logout(request: Request):
    # limpiar sesión
    request.session.clear()
    return RedirectResponse(url="/")
