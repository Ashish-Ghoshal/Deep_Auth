# middleware_setup.py

import logging
from starlette.middleware.sessions import SessionMiddleware

# This function is for middleware setup. It should only be called once
def initialize_middleware(app):
    """Setup all middleware for the application."""
    try:
        logging.info("Initializing session middleware.")
        app.add_middleware(SessionMiddleware, secret_key="!secret")
        logging.info("Middleware setup complete.")
    except Exception as e:
        logging.error(f"Error setting up middleware: {e}")
