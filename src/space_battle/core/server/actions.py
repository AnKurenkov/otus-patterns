import logging

from src.space_battle.core.actions.base import ActionBase
from src.space_battle.core.actions.game_actions import SchedulerAction
from src.space_battle.core.ioc import Ioc
from src.space_battle.core.server.server_thread import ServerThread

logger = logging.getLogger(__name__)


class HardStopAction(ActionBase):
    """Команда для немедленной остановки ServerThread"""

    def __init__(self, server_thread: ServerThread):
        self._server_thread = server_thread

    def execute(self):
        if self._server_thread.is_in_thread:
            self._server_thread.stop()
        else:
            raise Exception("Попытка остановить очередь из другого потока.")  # TODO: кастомное исключение


class SoftStopAction(ActionBase):
    """Команда для мягкой остановки ServerThread после обработки текущей очереди"""

    def __init__(self, server_thread: ServerThread):
        self._server_thread = server_thread

    def execute(self):
        old_behaviour = self._server_thread.behaviour

        def new_behaviour():
            if not self._server_thread.queue.empty():
                old_behaviour()
            else:
                if self._server_thread.is_in_thread:
                    self._server_thread.stop()
                else:
                    raise Exception("Попытка остановить очередь из другого потока.")  # TODO: кастомное исключение

        self._server_thread.behaviour = new_behaviour


class UseSchedulerAction(ActionBase):
    """Команда для включения использования Планировщика при обработке очереди в ServerThread"""

    def __init__(self, server_thread: ServerThread, scheduler: SchedulerAction):
        self._server_thread = server_thread
        self._scheduler = scheduler

    def execute(self):
        old_behaviour = self._server_thread.behaviour

        def new_behaviour():
            if not self._scheduler.has_work():
                old_behaviour()
            else:
                if not self._server_thread.queue.empty():
                    old_behaviour()
                    try:
                        self._scheduler.execute()
                    except Exception as e:
                        Ioc.resolve("HandleException", ActionBase, self._scheduler, e).execute()

        self._server_thread.behaviour = new_behaviour
