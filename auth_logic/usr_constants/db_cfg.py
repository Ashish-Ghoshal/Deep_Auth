from auth_logic.utils.util import CommonUtils

DB_URL_NEW = CommonUtils().get_env_var("DB_URL_NEW")
DB_NAME_NEW = CommonUtils().get_env_var("DB_NAME_NEW")
USR_COL_NEW = CommonUtils().get_env_var("USR_COL_NEW")
EMBED_COL_NEW = CommonUtils().get_env_var(
    "EMBED_COL_NEW"
)
