import os
import shutil
from pathlib import Path

from sgde_client import register, login, get_tasks


if __name__ == "__main__":
    instance_dir = Path(os.getcwd())

    os.system("flask --app sgde_server --debug run")

    os.environ["SGDE_SERVER_IP"] = "127.0.0.1"
    os.environ["SGDE_SERVER_PORT"] = "5000"

    register()
    login()

    get_tasks()

    shutil.rmtree(Path(instance_dir, "instance"))
