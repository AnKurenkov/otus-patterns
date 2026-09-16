from src.space_battle.auth_service.storage import create_game_repository
from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.scopes.init_app_scope_action import InitializeApplicationScopeAction


class RegisterAuthServiceDependenciesAction(ActionBase):
    """Регистрирует зависимости auth-сервиса в прикладном скоупе IoC.

    Запись выполняется прямо в прикладной скоуп, поэтому зависимость видна
    из любого дочернего скоупа потока и не сбрасывает текущий потоковый скоуп.
    """

    def execute(self):
        app_scope = InitializeApplicationScopeAction.get_application_scope()
        app_scope.setdefault("GameRepository", lambda: create_game_repository())
