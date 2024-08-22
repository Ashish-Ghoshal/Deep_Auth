import os, io, base64
from typing import List, Optional
from fastapi import APIRouter, File, Request
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from phases.auth_phase.user_authentikator import fetch_user_info  
from auth_logic.validation.au_processes import (
    ValidateLoginEmbed,
    ValidateRegisterEmbed,
)

app_handler = APIRouter(
    prefix="/app_routes",  # Unique route prefix
    tags=["application_process"],
    responses={"401": {"description": "Not Authorized"}},
)

tpl_renderer = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

# Environment variable change for GPU/CPU usage
os.environ["CUDA_PREFERENCE"] = "-1"

class ImageDataHandler:
    """Class to handle the processing and retrieval of image data from forms."""
    
    def __init__(self, req: Request):
        self.req = req
        self.image_slots = [None] * 8  # Different way to store image data

    async def extract_form_images(self):
        """Extract images from form data."""
        form_data = await self.req.form()
        self.image_slots = [form_data.get(f"img_{i+1}") for i in range(8)]  # Different naming pattern

async def redirect_if_not_authenticated(req: Request):
    """Redirect to login if user is not authenticated."""
    user_info = await fetch_user_info(req)
    if not user_info:
        return RedirectResponse(url="/auth_route", status_code=status.HTTP_302_FOUND)
    return user_info

@app_handler.get("/", response_class=HTMLResponse)
async def display_app_page(req: Request):
    try:
        user_details = await redirect_if_not_authenticated(req)
        return tpl_renderer.TemplateResponse(
            "embedded_login.html",
            context={"request": req, "status_code": status.HTTP_200_OK, "msg": "Login Successful", "user": user_details['username']}
        )
    except Exception as e:
        return tpl_renderer.TemplateResponse(
            "error_screen.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Login Embedding Failed"}
        )

@app_handler.post("/")
async def execute_login_embedding(req: Request):
    """Handles embedding process during login."""

    try:
        user_data = await redirect_if_not_authenticated(req)

        embed_validator = ValidateLoginEmbed(user_data["user_identifier"])

        image_processor = ImageDataHandler(req)
        await image_processor.extract_form_images()
        img_data_set = [convert_image_data(img) for img in image_processor.image_slots]

        if embed_validator.compare_stored_embeddings(img_data_set):
            return tpl_renderer.TemplateResponse(
                "embedded_login.html",
                status_code=status.HTTP_200_OK,
                context={"request": req, "status_code": status.HTTP_200_OK, "msg": "User Verified", "user": user_data['username']}
            )
        else:
            return tpl_renderer.TemplateResponse(
                "unauthorized_access.html",
                status_code=status.HTTP_404_NOT_FOUND,
                context={"status": False, 'status_code': status.HTTP_404_NOT_FOUND, "msg": "Authentication Unsuccessful"}
            )
    except Exception as e:
        return tpl_renderer.TemplateResponse(
            "unauthorized_access.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Error Processing Login Embedding"}
        )

@app_handler.get("/register_embed", response_class=HTMLResponse)
async def render_registration_page(req: Request):
    try:
        user_id = req.session.get("user_identifier")
        if user_id is None:
            return RedirectResponse(url="/auth_route", status_code=status.HTTP_302_FOUND)
        return tpl_renderer.TemplateResponse(
            "embedded_registration.html",
            context={"request": req, "status_code": status.HTTP_200_OK, "msg": "Proceed to Registration"}
        )
    except Exception as e:
        return tpl_renderer.TemplateResponse(
            "error_screen.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Error During Registration"}
        )

@app_handler.post("/register_embed")
async def execute_registration_embedding(req: Request):
    """Process and store user registration embedding."""

    try:
        user_id = req.session.get("user_identifier")
        if user_id is None:
            return RedirectResponse(url="/auth_route", status_code=status.HTTP_302_FOUND)
        
        image_processor = ImageDataHandler(req)
        await image_processor.extract_form_images()
        img_data_set = [convert_image_data(img) for img in image_processor.image_slots]
    
        reg_validator = ValidateRegisterEmbed(user_id)
        reg_validator.save_user_embeddings(img_data_set)

        return tpl_renderer.TemplateResponse(
            "login_screen.html",
            status_code=status.HTTP_200_OK,
            context={"request": req, "status": False, "msg": "Embedding Successfully Stored"}
        )
    except Exception as e:
        return tpl_renderer.TemplateResponse(
            "error_screen.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={"request": req, "status": False, "msg": "Error Storing Embedding"}
        )

def convert_image_data(data_uri):
    """Convert base64 image data to raw bytes."""
    return io.BytesIO(base64.b64decode(data_uri[data_uri.find(",") + 1:])).getvalue()
