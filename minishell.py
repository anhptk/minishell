#!/usr/bin/env python3

import os


class Minishell():
    def __init__(self):
        '''
        Create a new Minishell.
        '''
        self.name = 'intek-sh'
        self.command = ''
        self.args = []
        self.environ = os.environ.copy()
        self.exit = False
        self.valid_command = ['pwd', 'cd', 'printenv',
                              'export', 'unset', 'exit']
        self.home = ''

    def get_command(self):
        '''
        Get the command and its arguments to execute in Minishell.
        '''
        input_command = input(self.name + '$ ')
        self.args = input_command.strip().split(' ')
        self.command = self.args.pop(0)

    def pwd(self):
        return os.path.abspath('.')

    def check_valid_home(self):
        '''
        Check if home path is exist or not.
        '''
        try:
            self.home = self.environ['HOME']
        except KeyError:
            print(self.name + ': cd: HOME not set')
            return False

        if not os.path.isdir(self.home):
            print(self.name + ': cd: ' + self.home
                  + ': No such file or directory')
            return False

        return True

    def cd(self):
        # if no args, change the current directory to home
        if not self.args:
            if self.check_valid_home():
                os.chdir(self.home)
        elif len(self.args) > 1:
            print(self.name + ': cd: too many arguments')
        else:
            path = self.args[0]
            if path == '~':
                if self.check_valid_home():
                    os.chdir(self.home)
            elif os.path.exists(path):
                if os.path.isdir(path):
                    os.chdir(path)
                else:
                    print(self.name + ': cd: ' + path + ': Not a directory')
            else:
                print(self.name + ': cd: ' + path
                      + ': No such file or directory')

    def printenv(self):
        '''
        Print the environment variables if they exist in environ.
        '''
        try:
            if not self.args:
                for key, value in self.environ.items():
                    print(key + '=' + value)
            else:
                for key in self.args:
                    if key in self.environ.keys():
                        print(self.environ[key])
        # catch the key = None
        except TypeError:
            print(key + '=')

    def export(self):
        if not self.args:
            try:
                for key, value in self.environ.items():
                    print('declare -x', key + '="' + value + '"')
            # catch the key = None
            except TypeError:
                print('declare -x', key)

        else:
            for new_variable in self.args:
                equal = new_variable.find('=')

                # no key but have value
                if equal == 0:
                    print(self.name + ': export: `'
                          + new_variable + "': not a valid identifier")
                    pass

                # arg is a valid new key-value pair
                elif equal > 0:
                    key = new_variable[:equal]
                    try:
                        value = new_variable[equal+1:]
                    except IndexError:
                        value = ''
                    # add new item to dict
                    self.environ[key] = value
                else:
                    self.environ[new_variable] = None

    def unset(self):
        for del_key in self.args:
            if del_key in self.environ.keys():
                del self.environ[del_key]

    def quit(self):
        self.exit = True
        if not self.args:
            print('exit')
        elif len(self.args) > 1:
            print(self.name + ': exit: too many arguments')
        # if have only 1 arg
        else:
            try:
                print('exit')
                int(self.args[0])
            except ValueError:
                print('intek-sh: exit:', end='')

    def execute_command(self):
        if self.command == 'pwd':
            print(self.pwd())
        elif self.command == 'cd':
            self.cd()
        elif self.command == 'printenv':
            self.printenv()
        elif self.command == 'export':
            self.export()
        elif self.command == 'unset':
            self.unset()
        elif self.command == 'exit':
            self.quit()

    def execute_file(self):
        # get the command line to execute file
        if not self.args:
            command_line = self.command
        else:
            command_line = self.command + ' ' + ' '.join(self.args)
        # check if file can be read or not
        try:
            fd = os.open(self.command, os.O_RDONLY)
            os.close(fd)
        except PermissionError:
            print(self.name + ': ' + self.command + ': Permission denied')

        # check and execute file
        if not command_line.startswith('./'):
            command_line = './' + command_line
        os.system(command_line)


    def run_shell(self):
        '''
        Main loop of the program.
            Take the command then execute them repeatedly.
        '''
        while not self.exit:
            # get the command
            try:
                self.get_command()
            except EOFError:
                self.exit = True
                pass
                break

            # check if the command is valid:
            if not self.command:
                pass
            elif self.command in self.valid_command:
                self.execute_command()
            elif os.path.isfile(self.command):
                self.execute_file()
            else:
                print(self.name + ': ' + self.command + ': command not found')
