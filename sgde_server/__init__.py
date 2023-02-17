import yaml
import os
from pathlib import Path

from flask import Flask


# TODO must run on HTTPS
def create_app(config_filename=None, instance_path=None):
    if instance_path is not None:
        app = Flask(__name__, instance_path=instance_path)
    else:
        app = Flask(__name__)
    app.config.from_file(Path(app.root_path, "default_config.yml"), yaml.safe_load)

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
        app.config.from_file(Path(config_filename), yaml.safe_load)

    os.makedirs(app.instance_path, exist_ok=True)
    with open(Path(app.instance_path, "config.yml"), 'w') as f:
        yaml.dump(dict(app.config), f)

    return app
