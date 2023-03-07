import os

import uvicorn

from sgde_api_legacy.settings import get_settings
os.makedirs(get_settings().sgde_instance_path, exist_ok=True)
os.makedirs(get_settings().sgde_generator_path, exist_ok=True)

from sgde_api_legacy.database.db_app import Base, engine
Base.metadata.create_all(bind=engine)

from sgde_api_legacy.exchange import *
