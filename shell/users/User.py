from dataclasses import dataclass
from json import load, dump


@dataclass
class User:
    username: str
    password: str
    is_root: bool

    def save(self):
        users = load(open('shell/users/users.json', 'rb'))
        users[self.username] = dict(password=self.password, is_root=self.is_root)
        dump(users, open('shell/users/users.json', 'w'))

    @staticmethod
    def get_list():
        users = load(open('shell/users/users.json', 'rb'))
        return users
