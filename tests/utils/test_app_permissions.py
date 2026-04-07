import os
from src.utils.app_permissions import ActionsEnum, APP_PERMISSIONS, get_models

def test_actions_enum():
    assert ActionsEnum.CREATE == "CREATE"
    assert ActionsEnum.UPDATE == "UPDATE"
    assert ActionsEnum.DESTROY == "DESTROY"
    assert ActionsEnum.LIST == "LIST"
    assert ActionsEnum.GET == "GET"

def test_app_permissions_dict():
    assert APP_PERMISSIONS[ActionsEnum.CREATE] == "Create"
    assert APP_PERMISSIONS[ActionsEnum.UPDATE] == "Update"
    assert APP_PERMISSIONS[ActionsEnum.DESTROY] == "Destroy"
    assert APP_PERMISSIONS[ActionsEnum.LIST] == "List all"
    assert APP_PERMISSIONS[ActionsEnum.GET] == "Get One Record"

def test_get_models(tmp_path):
    # Create a temporary directory structure to test get_models
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "__init__.py").touch()
    (models_dir / "user.py").touch()
    (models_dir / "admin.py").touch()
    (models_dir / "role.py").touch()
    (models_dir / "not_a_model.txt").touch()

    models = get_models(str(models_dir))
    
    assert "user" in models
    assert "admin" in models
    assert "role" in models
    assert "__init__" not in models
    assert "not_a_model" not in models
    assert len(models) == 3
