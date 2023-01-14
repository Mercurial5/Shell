from typing import Protocol

from shell.users import User


class UserRepositoryInterface(Protocol):

    @staticmethod
    def create(username: str, password: str, is_root: bool = False) -> User: ...

    @staticmethod
    def get(username: str) -> User | None: ...


class UserRepository:

    @staticmethod
    def create(username: str, password: str, is_root: bool = False) -> User:
        user = User(username, password, is_root)
        user.save()
        return user

    @staticmethod
    def get(username: str) -> User | None:
        users = User.get_list()
        user = users.get(username)
        return User(username, user['password'], user['is_root']) if user else None
