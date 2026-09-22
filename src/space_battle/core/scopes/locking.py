import threading
from typing import Any, TypeAlias, cast

Scope: TypeAlias = dict[str, Any]

_FALLBACK_SCOPE_LOCK = threading.RLock()


def scope_lock(scope: Scope) -> threading.RLock:
    """Per-scope RLock для атомарного доступа к словарю скоупа.

    Лок создаётся вместе со скоупом и хранится под зарезервированным ключом
    "IoC.Scope.Lock". Если у скоупа его нет, используется общий fallback-лок.
    """
    lock = scope.get("IoC.Scope.Lock")
    return cast(threading.RLock, lock if lock is not None else _FALLBACK_SCOPE_LOCK)
