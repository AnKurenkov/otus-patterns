from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.space_battle.core.actions.base import ActionsLoopBase


class ActionsLoopStateBase(ABC):
    """
    Абстрактное состояние конечного автомата, определяющего режим обработки
    очереди команд (паттерн "Состояние").

    Конкретная реализация задаёт, как именно обрабатывается очередная команда,
    извлечённая из очереди (выполняется, перенаправляется и т.д.), и в какое
    состояние автомат должен перейти дальше.

    Код, работающий с состояниями (ActionsLoop/ServerThread, другие состояния),
    должен зависеть только от этого абстрактного класса и не должен знать
    о конкретных реализациях состояний.
    """

    @abstractmethod
    def handle(self, actions_loop: "ActionsLoopBase") -> Optional["ActionsLoopStateBase"]:
        """
        Извлекает и обрабатывает очередную команду из очереди `actions_loop.queue`
        в соответствии с текущим режимом обработки.

        :param actions_loop: цикл обработки очереди команд (ActionsLoop/ServerThread),
            предоставляющий доступ к очереди команд.
        :return: следующее состояние конечного автомата, с которого будет обрабатываться
            следующая команда. None означает, что поток обработки команд должен
            быть остановлен.
        """
