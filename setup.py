from setuptools import setup, find_packages
from typing import List
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("SetupLogger")

# Project metadata
PROJ_TITLE = "Face Authenticator"  
VER_NUM = "0.0.1"
AUTHOR_NAME = "Ashish Ghoshal"
PROJECT_DESC = "This is a Face Authenticator Project"


# Setting up the package with the above information

setup(
    name=PROJ_TITLE,
    version=VER_NUM,
    author=AUTHOR_NAME,
    description=PROJECT_DESC,
    packages=find_packages(),
)

log.info("Setup script executed successfully.")
