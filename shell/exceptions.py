class ShellBaseException(Exception):
    pass


class PathNotFound(ShellBaseException):
    pass


class PathIsNotDir(ShellBaseException):
    pass


class PathIsNotFile(ShellBaseException):
    pass


class IsDir(ShellBaseException):
    pass


class NotAllowed(ShellBaseException):
    pass
