from flask import Flask

from src.space_battle.auth_service.dependencies import RegisterAuthServiceDependenciesAction
from src.space_battle.auth_service.routes import router
from src.space_battle.config import settings
from src.space_battle.core.scopes.init_action import InitAction
from src.space_battle.core.scopes.init_app_scope_action import InitializeApplicationScopeAction

app = Flask(__name__)
app.register_blueprint(router)


if __name__ == "__main__":
    InitAction().execute()
    InitializeApplicationScopeAction().execute()
    RegisterAuthServiceDependenciesAction().execute()
    app.run(host=settings.auth_service_host, port=settings.auth_service_port)
