# route_setup.py

import logging
from phases.app_phase import application
from phases.auth_phase import user_authentikator

# Here we set up all routes. Not much else to do here.
def configure_routes(app):
    """Add routes to the FastAPI application."""
    try:
        logging.info("Adding authentication routes.")
        app.include_router(user_authentikator.rtr)
        
        logging.info("Adding application routes.")
        app.include_router(application.app_router)
        
        logging.info("Routes setup complete.")
    except Exception as e:
        logging.error(f"Error setting up routes: {e}")
