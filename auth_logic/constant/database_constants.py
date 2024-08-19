from auth_logic.utils.util import CommonUtils

MONGODB_URL_KEY = CommonUtils().get_env_var("MONGODB_URL_KEY")
DATABASE_NAME = CommonUtils().get_env_var("DATABASE_NAME")
USER_COLLECTION_NAME = CommonUtils().get_env_var("USER_COLLECTION_NAME")
EMBEDDING_COLLECTION_NAME = CommonUtils().get_env_var(
    "EMBEDDING_COLLECTION_NAME"
)
