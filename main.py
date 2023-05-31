from functions import greeting, print_instructions, parser_commands, handler


def main():
    greeting()
    print_instructions()
    while True:
        text = input('\nEnter your command: ')
        command, parameter = parser_commands(text)
        try:
            func = handler(command)
            func(parameter) if parameter else func()
        except (TypeError, KeyError):
            print('I do not understand what you want to do. Please look at the commands.')


if __name__ == '__main__':
    main()
