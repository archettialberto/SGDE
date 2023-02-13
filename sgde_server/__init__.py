import json
import os
from pathlib import Path

from flask import Flask


def create_app(config_filename=None):
    app = Flask(__name__)
    app.config.from_file(Path(app.root_path, "default_config.json"), json.load)

    from sgde_server.db import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from sgde_server.auth import auth, jwt
    jwt.init_app(app)
    app.register_blueprint(auth)

    from sgde_server.exchange import exchange
    app.register_blueprint(exchange)

    if config_filename:
        app.config.from_json(Path(config_filename))

    os.makedirs(app.instance_path, exist_ok=True)
    with open(Path(app.instance_path, "config.json"), 'w') as f:
        json.dump(dict(app.config), f, indent=2, default=str)

    return app
