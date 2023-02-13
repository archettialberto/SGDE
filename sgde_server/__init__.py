import os

from flask import Flask

from .args import Args


def create_app(config_filename=Args.CONFIG_FILENAME):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    if not os.path.isfile(os.path.join(app.instance_path, Args.CONFIG_FILENAME)):
        raise FileNotFoundError(f"File {os.path.join(app.instance_path, Args.CONFIG_FILENAME)} not found")
    app.config.from_mapping(Args.BASE_APP_CONFIG)
    app.config.from_pyfile(config_filename)

    from sgde_server.db import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from sgde_server.auth import auth, jwt
    jwt.init_app(app)
    app.register_blueprint(auth)

    from sgde_server.exchange import exchange
    app.register_blueprint(exchange)

    return app
