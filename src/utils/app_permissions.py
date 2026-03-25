from enum import Enum
import os


class ActionsEnum(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DESTROY = "DESTROY"
    LIST = "LIST"
    GET = "GET"
   
APP_PERMISSIONS: dict[ActionsEnum, str] = {
   ActionsEnum.CREATE: "Create",
   ActionsEnum.UPDATE: "Update",
   ActionsEnum.DESTROY: "Destroy",
   ActionsEnum.LIST: "List all",
   ActionsEnum.GET: "Get One Record",
}

def get_models(path="src/models"):
    return [
        filename[:-3]  # remove '.py'
        for filename in os.listdir(path)
        if filename.endswith(".py") and filename != "__init__.py"
    ]