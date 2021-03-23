from src.exceptions import LocalProjectBaseException


class FatalException(LocalProjectBaseException):
    pass


class GameEventException(LocalProjectBaseException):
    pass


class InvalidPlayerAction(GameEventException):
    pass


class PlayerHasWon(GameEventException):
    pass


class GameHasEnded(GameEventException):
    pass


class GameIsFull(GameEventException):
    pass


class LogicalError(GameEventException):
    pass
