# main_entry.py

import os
import uvicorn
import logging
from fastapi import FastAPI, Response
from starlette import status
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from utility.middleware_setup import initialize_middleware
from utility.route_setup import configure_routes

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_app() -> FastAPI:
    """Build and returns the FastAPI application object."""
    logging.info("Starting up the FastAPI application...")
    
    app = FastAPI()
    
    # Mount static files to serve static content
    app.mount("/static", StaticFiles(directory='static_files'), name="static_content")
    
    # Initialize middleware and routes
    initialize_middleware(app)
    configure_routes(app)
    
    logging.info("Middleware and routes have been set up successfully.")

    @app.get("/")
    def redirect_to_auth():
        """Redirects to the authentication page"""
        try:
            logging.info("Redirecting user to the authentication page.")
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        except Exception as e:
            logging.error(f"An error occurred during redirection: {e}")
            return Response("Server error, please try again later.", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return app

if __name__ == "__main__":
    fastapi_app = build_app()
    logging.info("Running the FastAPI application.")
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8080)
