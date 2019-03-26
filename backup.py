#!/usr/bin/env python3
import os


def get_command():
    # sys.stdout.write('intek-sh$ ')
    input_command = input('intek-sh$ ')
    args = input_command.strip().split(' ')
    command = args.pop(0)
    return command, args


def pwd():
    return os.path.abspath('.')


def cd_check_home(environ_dict):
    try:
        home = environ_dict['HOME']
    except KeyError:
        print('intek-sh: cd: HOME not set')
        return False

    if not os.path.isdir(home):
        print('intek-sh: cd: ' + home + ': No such file or directory')
        return False
    return home


def cd(args, environ_dict):
    # check if HOME is exists or not

    if not args:
        # back to home directory
        home = cd_check_home(environ_dict)
        if home:
            os.chdir(home)
    elif len(args) > 1:
        print('intek-sh: cd: too many arguments')
    else:
        # check if it a valid disk, then move and change path
        path = args[0]
        if path == '~':
            home = cd_check_home(environ_dict)
            if home:
                os.chdir(home)
        elif os.path.exists(path):
            if not os.path.isdir(path):
                print('intek-sh: cd: ' + path + ': Not a directory')
            else:
                os.chdir(path)
        else:
            print('intek-sh: cd: ' + path + ': No such file or directory')


def printenv(args):
    if not args:
        for key, value in environ_dict.items():
            print(key + '=' + value)
    else:
        for key in args:
            if key in environ_dict.keys():
                print(environ_dict[key])


def export(args, environ_dict):
    if not args:
        for key, value in environ_dict.items():
            print('declare -x', key + '="' + value + '"')
    else:
        for new_item in args:
            pointer = new_item.find('=')
            if pointer == 0:
                print('intek-sh: export: `'
                      + new_item + "': not a valid identifier")
                break
            elif pointer > 0:
                key = new_item[:pointer]
                try:
                    value = new_item[pointer+1:]
                except IndexError:
                    value = ''
                environ_dict[key] = value
            else:
                pass
    return environ_dict


def unset(args, environ_dict):
    for del_item in args:
        if del_item in environ_dict.keys():
            del environ_dict[del_item]
    return environ_dict


def exit_shell(args):
    if not args:
        print('exit')
    elif len(args) > 1:
        print('intek-sh: exit: too many arguments')
    else:
        try:
            print('exit')
            int(args[0])
        except ValueError:
            print('intek-sh: exit:', end='')


environ_dict = os.environ.copy()
while True:
    try:
        command, args = get_command()
    except EOFError:
        break

    if not command:
        pass
    elif command == 'exit':
        exit_shell(args)
        break
    else:
        if command == 'pwd':
            print(pwd())
        elif command == 'cd':
            cd(args, environ_dict)
        elif command == 'printenv':
            printenv(args)
        elif command == 'export':
            environ_dict = export(args, environ_dict)
        elif command == 'unset':
            environ_dict = unset(args, environ_dict)
        elif os.path.isfile(command):
            # get the command line to execute file
            if not args:
                command_line = command
            else:
                command_line = command + ' ' + ' '.join(args)
            # check if file can be read or not
            try:
                fd = os.open(command, os.O_RDONLY)
                os.close(fd)
                # check and execute file
                if not command_line.startswith('./'):
                    command_line = './' + command_line
                os.system(command_line)
            except PermissionError:
                print('intek-sh: ' + command + ': command not found')

        else:
            print('intek-sh: ' + command + ': command not found')
