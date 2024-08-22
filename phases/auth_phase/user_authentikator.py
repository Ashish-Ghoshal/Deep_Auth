# user_authentikator.py

import os
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi import HTTPException, status, APIRouter, Request, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

from auth_logic.usr_entities.usr_data_entity import UserData
from auth_logic.validation.validation_process import ValidateRegister, ValidateLogin
from auth_logic.usr_constants.auth_cfg import SECRET_KEY, ALGORITHM

template_loader = Jinja2Templates(directory=os.path.join(os.getcwd(), "viewpages"))

auth_router = APIRouter(
    prefix="/userauth",
    tags=["user_authentik"],
    responses={"401": {"description": "Unauthorized"}},
)

async def fetch_user_details(req: Request):
    token = req.cookies.get("access_token")
    if not token:
        return None

    return decode_jwt_token(token)

async def decode_jwt_token(token: str):
    try:
        data = jwt.decode(token, SECURE_KEY, algorithms=[ENCRYPTION_ALGO])
        user_id = data.get("sub")
        uname = data.get("username")
        if not user_id or not uname:
            return None
        return {"uuid": user_id, "username": uname}
    except JWTError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Error decoding token: {e}"})

def generate_access_token(user_id: str, uname: str, exp_delta: Optional[timedelta] = None) -> str:
    payload = create_token_payload(user_id, uname, exp_delta)
    return jwt.encode(payload, SECURE_KEY, algorithm=ENCRYPTION_ALGO)

def create_token_payload(user_id: str, uname: str, exp_delta: Optional[timedelta]) -> dict:
    expire = datetime.utcnow() + (exp_delta if exp_delta else timedelta(minutes=15))
    return {"sub": user_id, "username": uname, "exp": expire}

@auth_router.post("/token_auth")
async def login_with_token(resp: Response, login_data) -> dict:
    user_val = ValidateLogin(login_data['email'], login_data['password'])
    user = user_val.authenticate_user()
    if not user:
        return {"status": False, "uuid": None, "response": resp}
    
    token_exp = timedelta(minutes=15)
    token = generate_access_token(user["UUID"], user["username"], exp_delta=token_exp)
    resp.set_cookie(key="access_token", value=token, httponly=True)
    return {"status": True, "uuid": user["UUID"], "response": resp}

@auth_router.get("/", response_class=HTMLResponse)
async def display_login_page(req: Request):
    return load_template("login.html", req, "login_page")

def load_template(template_name: str, req: Request, msg: str):
    try:
        return template_loader.TemplateResponse(template_name, context={"request": req, "msg": msg, "status_code": status.HTTP_200_OK})
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

@auth_router.post("/process_reg")
async def process_user_registration(req: Request):
    form = RegistrationForm(req)
    await form.populate_form()
    new_user = Usr(form.name, form.uname, form.email, form.phone, form.pwd1, form.pwd2)
    req.session["uuid"] = new_user.uid

    user_val = ValidateRegister(new_user)
    validation_result = user_val.validate()

    if not validation_result["status"]:
        return load_template("login.html", req, validation_result["msg"])

    user_val.save_user()
    return RedirectResponse(url="/app/register_embedding", status_code=status.HTTP_302_FOUND, headers={"uuid": new_user.uid})

@auth_router.get("/logout_user")
async def logout_user(req: Request):
    resp = RedirectResponse(url="/userauth/", status_code=status.HTTP_302_FOUND, headers={"msg": "Logged out"})
    resp.delete_cookie(key="access_token")
    return resp
