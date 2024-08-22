from auth_logic.utils.util import CommonUtils


SECRET_KEY = CommonUtils().get_env_var("SECRET_KEY")
ALGORITHM = CommonUtils().get_env_var("ALGORITHM")
