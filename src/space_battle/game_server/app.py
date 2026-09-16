from flask import Flask

from src.space_battle.config import settings
from src.space_battle.core.scopes.init_action import InitAction
from src.space_battle.core.scopes.init_app_scope_action import InitializeApplicationScopeAction
from src.space_battle.game_server.game_runtime import get_game_runtime
from src.space_battle.game_server.routes import router

app = Flask(__name__)
app.register_blueprint(router)


if __name__ == "__main__":
    InitAction().execute()
    InitializeApplicationScopeAction().execute()
    get_game_runtime()
    app.run(host=settings.game_service_host, port=settings.game_service_port)
