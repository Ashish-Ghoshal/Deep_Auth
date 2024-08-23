

import logging

import setuptools

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("SetupLogger")

# Project metadata
TITLE = "Facial Verification"  
NUM = "0.1.5"
NAME = "Ashish Ghoshal"
SUMM = "Facial Verification"


# Setting up the package with the above information

setuptools.setup(
    name=TITLE,
    version=NUM,
    author=NAME,
    description=SUMM,
    packages=setuptools.find_packages(),
)

log.info("Setup script executed successfully.")
