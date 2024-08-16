import os
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi import HTTPException, status, APIRouter, Request, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

from face_auth.entity.user import User
from face_auth.business_val.user_val import RegisterVal, LoginVal
from face_auth.constant.auth_constant import SECRET_KEY, ALGORITHM

tpls = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

class LoginForm:
    def __init__(self, req: Request):
        self.req: Request = req
        self.email: Optional[str] = None
        self.pwd: Optional[str] = None
    
    async def load_form(self):
        form_data = await self.req.form()
        self.email = form_data.get("email")
        self.pwd = form_data.get("password")

class RegisterForm:
    def __init__(self, req: Request):
        self.req: Request = req
        self.name: Optional[str] = None
        self.uname: Optional[str] = None
        self.email: Optional[str] = None
        self.phone: Optional[int] = None
        self.pwd1: Optional[str] = None
        self.pwd2: Optional[str] = None
        
    async def load_form(self):
        form_data = await self.req.form()
        self.name = form_data.get("name")
        self.uname = form_data.get("username")
        self.email = form_data.get("email")
        self.phone = form_data.get("ph_no")
        self.pwd1 = form_data.get("password1")
        self.pwd2 = form_data.get("password2")

rtr = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={"401": {"description": "Unauthorized"}},
)

# Fetch logged-in user details
async def fetch_current_user(req: Request):
    try:
        secret = SECRET_KEY
        algo = ALGORITHM
        token = req.cookies.get("access_token")
        if not token:
            return None

        data = jwt.decode(token, secret, algorithms=[algo])
        user_id: str = data.get("sub")
        uname: str = data.get("username")

        if not user_id or not uname:
            return logout(req)
        return {"uuid": user_id, "username": uname}
    except JWTError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as ex:
        msg = "Error fetching user"
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": msg})

def gen_access_token(user_id: str, uname: str, exp_delta: Optional[timedelta] = None) -> str:
    try:
        secret = SECRET_KEY
        algo = ALGORITHM
        payload = {"sub": user_id, "username": uname}
        expire = datetime.utcnow() + (exp_delta if exp_delta else timedelta(minutes=15))
        payload.update({"exp": expire})
        return jwt.encode(payload, secret, algorithm=algo)
    except Exception as ex:
        raise ex

@rtr.post("/token")
async def login_with_token(resp: Response, login_data) -> dict:
    try:
        user_val = LoginVal(login_data['email'], login_data['password'])
        user: Optional[str] = user_val.auth_user()
        if not user:
            return {"status": False, "uuid": None, "response": resp}
        token_exp = timedelta(minutes=15)
        token = gen_access_token(user["UUID"], user["username"], exp_delta=token_exp)
        resp.set_cookie(key="access_token", value=token, httponly=True)
        return {"status": True, "uuid": user["UUID"], "response": resp}
    except Exception as ex:
        msg = "Token generation failed"
        return {"status": False, "uuid": None, "response": JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": msg})}

@rtr.get("/", response_class=HTMLResponse)
async def show_login_page(req: Request):
    try:
        return tpls.TemplateResponse("login.html", context={"request": req, "msg": "login_page", "status_code": status.HTTP_200_OK})
    except Exception as ex:
        raise ex

@rtr.post("/", response_class=HTMLResponse)
async def handle_login(req: Request):
    try:
        form = LoginForm(req)
        await form.load_form()
        login_data = {"email": form.email, "password": form.pwd}
        resp = RedirectResponse(url="/application/", status_code=status.HTTP_302_FOUND)
        token_resp = await login_with_token(response=resp, login=login_data)

        if not token_resp["status"]:
            return tpls.TemplateResponse("login.html", 
                                         context={"request": req, "msg": "Invalid credentials", "status_code": status.HTTP_404_NOT_FOUND},
                                         status_code=status.HTTP_401_UNAUTHORIZED)
        resp.headers["uuid"] = token_resp["uuid"]
        return resp
    except HTTPException:
        return tpls.TemplateResponse("login.html", status_code=status.HTTP_401_UNAUTHORIZED,
                                     content={"request": req, "status": False, "message": "Unknown error"})
    except Exception as ex:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "User not found"})

@rtr.get("/register", response_class=HTMLResponse)
async def show_register_page(req: Request):
    try:
        return tpls.TemplateResponse("login.html", status_code=status.HTTP_200_OK,
                                     context={"request": req, "message": "Registration Page"})
    except Exception as ex:
        raise ex

@rtr.post("/register", response_class=HTMLResponse)
async def handle_registration(req: Request):
    try:
        form = RegisterForm(req)
        await form.load_form()
        new_user = User(form.name, form.uname, form.email, form.phone, form.pwd1, form.pwd2)
        req.session["uuid"] = new_user.uid

        user_val = RegisterVal(new_user)
        val_result = user_val.validate()

        if not val_result["status"]:
            return tpls.TemplateResponse("login.html",
                                         status_code=status.HTTP_401_UNAUTHORIZED,
                                         context={"request": req, "msg": val_result["msg"], "status_code": status.HTTP_404_NOT_FOUND})

        user_val.save_user()
        return RedirectResponse(url="/application/register_embedding", status_code=status.HTTP_302_FOUND,
                                headers={"uuid": new_user.uid})
    except Exception as ex:
        return tpls.TemplateResponse("error.html", status_code=status.HTTP_404_NOT_FOUND,
                                     context={"request": req, "status": False})

@rtr.get("/logout")
async def logout(req: Request):
    try:
        resp = RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND, headers={"msg": "Logged out"})
        resp.delete_cookie(key="access_token")
        return resp
    except Exception as ex:
        raise ex
