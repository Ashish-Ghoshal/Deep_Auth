import os
from datetime import datetime

from auth_logic.constant.database_constants import *

PIPELINE_NAME = "face"
PIPELINE_ARTIFACT_DIR = os.path.join(os.getcwd(), "finance_artifact")

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
