import threading
from typing import Any, Callable, Optional, TypeAlias

Scope: TypeAlias = dict[str, Callable[[list], Any]]


# TODO: написать тесты
class ThreadScopeContext:
    """Хранилище текущих скоупов для каждого потока"""

    _local = threading.local()

    @classmethod
    def get_current_scope(cls) -> Optional[Scope]:
        return getattr(cls._local, "scope", None)

    @classmethod
    def set_current_scope(cls, scope: Scope) -> None:
        cls._local.scope = scope

    @classmethod
    def clear_current_scope(cls) -> None:
        if hasattr(cls._local, "scope"):
            delattr(cls._local, "scope")
