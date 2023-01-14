import os
import shutil

from shell import exceptions
from shell.users import User, UserServiceInterface, UserService, exceptions as user_exceptions
from shell.utils import Colors


class Shell:

    def __init__(self, user: User):
        self.executor = self.CommandExecutor(user)
        self.list_of_commands = [command for command in dir(self.executor) if not command.startswith('_')]

    def execute_command(self):
        current_path = self.executor.path
        command, *args = input(f'{current_path}> ').split()

        flags = [i for i in args if i.startswith('-')]
        args = [i for i in args if i not in flags]

        if command not in self.list_of_commands:
            self.executor.echo(f'{command}: Command not found.')
            return

        command_function = self.executor.__getattribute__(command)
        try:
            command_function(*(tuple(args) + tuple(flags)))
        except exceptions.ShellBaseException as e:
            print(f'{Colors.fail}{e}{Colors.default}')
        except TypeError:
            print(f'{Colors.fail}Not enough arguments for command {command}{Colors.default}')

    class CommandExecutor:
        def __init__(self, user: User):
            self.user_service: UserServiceInterface = UserService()
            self.user = user
            self.path = 'root' if user.is_root else os.path.join('home', user.username)
            self.base_path = os.path.join(os.getcwd(), 'playground')
            self.full_path = os.path.join(self.base_path, self.path)

        def ls(self, path: str = None):
            full_path = self.full_path if path is None else os.path.join(self.full_path, path)
            relative_path = self.path if path is None else os.path.join(self.path, path)

            self._is_exists(full_path, relative_path)
            self._is_dir(full_path, relative_path)

            for file in os.scandir(full_path):
                color = Colors.file if os.path.isfile(file) else Colors.directory
                print(f'{color}{file.name}{Colors.default}', end=' ')
            print()

        def cd(self, path: str):
            full_path = os.path.dirname(self.full_path) if path == '..' else os.path.join(self.full_path, path)
            relative_path = os.path.dirname(self.path) if path == '..' else os.path.join(self.path, path)

            self._is_exists(full_path, relative_path)
            self._is_dir(full_path, relative_path)

            if self.path == '' and path == '..':
                return

            if self.path == '' and path == 'root' and not self.user.is_root:
                raise exceptions.NotAllowed('User does not have permission for this operation')

            if self.path == 'home' and path != self.user.username and not self.user.is_root:
                raise exceptions.NotAllowed('User does not have permission for this operation')

            self.full_path, self.path = full_path, relative_path

        def mkdir(self, dirname: str):
            os.mkdir(os.path.join(self.full_path, dirname))

        def touch(self, filename: str):
            open(os.path.join(self.full_path, filename), 'w').close()

        def rm(self, path: str, flag: str = None):
            full_path = os.path.join(self.full_path, path)
            relative_path = os.path.join(self.path, path)

            self._is_exists(full_path, relative_path)

            if self._is_dir(full_path, relative_path, exception=False):
                if flag is not None and flag == '-r':
                    shutil.rmtree(full_path)
                    return
                else:
                    raise exceptions.IsDir(f'Path {path} is a directory. Use -r flag')

            os.remove(full_path)

        def mv(self, target: str, destination: str):
            full_target_path = os.path.join(self.full_path, target)
            full_destination_path = os.path.join(self.full_path, destination)

            if self._is_dir(full_destination_path, '', exception=False):
                full_destination_path = os.path.join(full_destination_path, target)
            elif self._is_exists(full_destination_path, '', exception=False):
                self.rm(destination)

            os.rename(full_target_path, full_destination_path)

        def cat(self, path: str):
            full_target_path = os.path.join(self.full_path, path)
            relative_target_path = os.path.join(self.path, path)

            self._is_file(full_target_path, relative_target_path)

            with open(full_target_path, 'r', encoding='utf-8') as file:
                content = file.read()

            self.echo(content)

        def adduser(self):
            if not self.user.is_root:
                raise exceptions.NotAllowed('User does not have permission for this operation')

            username, password = input('Enter username: '), input('Enter password: ')

            try:
                self.user_service.adduser(username, password)
            except user_exceptions.UserAlreadyExists as e:
                print(f'{Colors.fail}{e}{Colors.default}')
                return

            path = os.path.join(self.base_path, 'home', username)
            os.mkdir(path)

        @staticmethod
        def echo(content: str):
            print(content)

        @staticmethod
        def exit():
            exit(1)

        @staticmethod
        def _is_exists(full_path: str, relative_path: str, exception: bool = True) -> bool:
            if not os.path.exists(full_path):
                if exception:
                    raise exceptions.PathNotFound(f'Path {relative_path} not found.')
                return False

            return True

        @staticmethod
        def _is_dir(full_path: str, relative_path: str, exception: bool = True) -> bool:
            if not os.path.isdir(full_path):
                if exception:
                    raise exceptions.PathIsNotDir(f'Path {relative_path} is not a directory')
                return False

            return True

        @staticmethod
        def _is_file(full_path: str, relative_path: str, exception: bool = True) -> bool:
            if not os.path.isfile(full_path):
                if exception:
                    raise exceptions.PathIsNotFile(f'Path {relative_path} is not a file')
                return False

            return True
