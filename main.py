from shell import Shell
from shell.users import UserService


def main():
    username, password = input('Enter username: '), input('Enter password: ')

    user_service = UserService()
    user = user_service.login(username, password)

    if user is None:
        print('User with these credentials not found.')
        return

    shell = Shell(user)

    while True:
        shell.execute_command()


if __name__ == '__main__':
    main()
