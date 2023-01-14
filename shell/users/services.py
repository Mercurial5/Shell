from typing import Protocol

from shell.users import User, UserRepositoryInterface, UserRepository, exceptions


class UserServiceInterface(Protocol):
    repo: UserRepositoryInterface

    @staticmethod
    def adduser(username: str, password: str, is_root: bool = False) -> User: ...

    def login(self, username: str, password: str) -> User | None: ...

    def _get_user(self, username: str) -> User | None: ...


class UserService:

    def __init__(self):
        self.repo: UserRepositoryInterface = UserRepository()

    def adduser(self, username: str, password: str, is_root: bool = False) -> User:
        if self._get_user(username) is None:
            return self.repo.create(username, password, is_root)

        raise exceptions.UserAlreadyExists(f'User with username {username} already exists')

    def login(self, username: str, password: str) -> User | None:
        if user := self._get_user(username):
            return user if user.password == password else None

        return None

    def _get_user(self, username: str) -> User | None:
        return self.repo.get(username)
