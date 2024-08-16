import os, io, base64
from typing import List, Optional
from fastapi import APIRouter, File, Request
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from controller.auth_controller.authentication import get_current_user
from face_auth.business_val.user_embedding_val import (
    UserLoginEmbeddingValidation,
    UserRegisterEmbeddingValidation,
)

app_router = APIRouter(
    prefix="/app",
    tags=["app"],
    responses={"401": {"description": "Unauthorized"}},
)
template_loader = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

class ImgForm:
    def __init__(self, req: Request):
        self.req: Request = req
        self.img1: Optional[str] = None
        self.img2: Optional[str] = None
        self.img3: Optional[str] = None
        self.img4: Optional[str] = None
        self.img5: Optional[str] = None
        self.img6: Optional[str] = None
        self.img7: Optional[str] = None
        self.img8: Optional[str] = None

    async def load_form_data(self):
        form_data = await self.req.form()
        self.img1 = form_data.get("image1")
        self.img2 = form_data.get("image2")
        self.img3 = form_data.get("image3")
        self.img4 = form_data.get("image4")
        self.img5 = form_data.get("image5")
        self.img6 = form_data.get("image6")
        self.img7 = form_data.get("image7")
        self.img8 = form_data.get("image8")

@app_router.get("/", response_class=HTMLResponse)
async def show_app(req: Request):
    try:
        user = await get_current_user(req)
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        return template_loader.TemplateResponse(
            "login_embedding.html",
            context={"request": req, "status_code": status.HTTP_200_OK, "msg": "Login Successful", "user": user['username']}
        )
    except Exception as e:
        return template_loader.TemplateResponse(
            "error.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Error in Login Embedding"}
        )

@app_router.post("/")
async def login_embedding(req: Request):
    """Handles user login embedding"""

    try:
        user = await get_current_user(req)
        if user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

        login_val = UserLoginEmbeddingValidation(user["uuid"])

        form = ImgForm(req)
        await form.load_form_data()
        images = []
        img_list = [form.img1, form.img2, form.img3, form.img4, form.img5, form.img6, form.img7, form.img8]

        for img in img_list:
            img_data = img[img.find(",") + 1:]
            img_bytes = io.BytesIO(base64.b64decode(img_data)).getvalue()
            images.append(img_bytes)

        if login_val.compareEmbedding(images):
            return template_loader.TemplateResponse(
                "login_embedding.html",
                status_code=status.HTTP_200_OK,
                context={"request": req, "status_code": status.HTTP_200_OK, "msg": "User Authenticated", "user": user['username']}
            )
        else:
            return template_loader.TemplateResponse(
                "unauthorized.html",
                status_code=status.HTTP_404_NOT_FOUND,
                context={"status": False, 'status_code': status.HTTP_404_NOT_FOUND, "msg": "Authentication Failed"}
            )
    except Exception as e:
        return template_loader.TemplateResponse(
            "unauthorized.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Login Embedding Error"}
        )

@app_router.get("/register_embedding", response_class=HTMLResponse)
async def show_register_embedding(req: Request):
    try:
        user_id = req.session.get("uuid")
        if user_id is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        return template_loader.TemplateResponse(
            "register_embedding.html",
            context={"request": req, "status_code": status.HTTP_200_OK, "msg": "Login Successful"}
        )
    except Exception as e:
        return template_loader.TemplateResponse(
            "error.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Error in Register Embedding"}
        )

@app_router.post("/register_embedding")
async def register_embedding(req: Request):
    """Handles user registration embedding"""

    try:
        user_id = req.session.get("uuid")
        if user_id is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        
        form = ImgForm(req)
        await form.load_form_data()
        images = []
        img_list = [form.img1, form.img2, form.img3, form.img4, form.img5, form.img6, form.img7, form.img8]

        for img in img_list:
            img_data = img[img.find(",") + 1:]
            img_bytes = io.BytesIO(base64.b64decode(img_data)).getvalue()
            images.append(img_bytes)
    
        reg_val = UserRegisterEmbeddingValidation(user_id)
        reg_val.saveEmbedding(images)

        return template_loader.TemplateResponse(
            "login.html",
            status_code=status.HTTP_200_OK,
            context={"request": req, "status": False, "msg": "Embedding Stored Successfully"}
        )
    except Exception as e:
        return template_loader.TemplateResponse(
            "error.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Error in Storing Embedding"}
        )

