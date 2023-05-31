import re
from datetime import datetime
import json
from classes_con_assist import Record, AddressBook, contacts_new, DateFormatEncoder
import sys


def input_error(func):
    def inner_func(par=None):
        try:
            res = func(par)
            return res
        except (KeyError, ValueError, IndexError, TypeError) as error:
            print(f'Error: {error}. Please check the accordance of the entered data to the requirements.\n'
                  f'And also a correctness of the entered name or/and phone number. And, of course, their existence.')
    return inner_func


def add_cont(name: str):
    record = Record(name)
    contacts_new.add_record(record)
    print(f'New contact {name} was added.')


@input_error
def delete_cont(name: str):
    contacts_new.delete_record(search_in(name))
    print(f'The contact {name} was deleted.')


def search(key: str):
    contacts_new.search(key)


def show_contacts():
    res = contacts_new.iterator()
    for records in res:
        for name, info in records.items():
            print(f'{name}: {info}')
        input('Press any key')


@input_error
def change_name(name: str):
    name_ = search_in(name)
    new_name: str = input('Enter a new name for the contact: ')
    contacts_new.change_name(name_, new_name)
    print('A name of the contact was changed.')


@input_error
def add_phone_num(name: str):
    name = search_in(name)
    phone_num = input('Enter a phone number to add to the contact: ')
    contacts_new[name].add_number(phone_num)
    print(f'The phone number was added to contact {name}')


@input_error
def change_phone_num(name: str):
    name = search_in(name)
    phone_num = input('Enter <an old phone number>-<new phone number> for the contact: ')
    old, new = phone_num.strip().split('-')
    contacts_new.data[name].change_number(old, new)
    print(f'The phone number of the contact {name} was changed.')


@input_error
def delete_phone_num(name: str):
    name = search_in(name)
    phone_num = input('Enter a phone number to delete from the contact: ')
    contacts_new[name].delete_number(phone_num)
    print(f'The phone number of the contact {name} was deleted.')


@input_error
def change_email(name: str):
    name = search_in(name)
    email = input('Enter an email address for the contact: ')
    contacts_new[name].add_change_email(email)
    print(f'The email of the contact {name} was changed')


@input_error
def change_date_bd(name: str):
    name = search_in(name)
    date_bd = input('Enter a date of birth according a pattern <YYYY MM DD>: ')
    year, month, day = date_bd.strip().split(' ')
    contacts_new[name].add_bd((int(year), int(month), int(day)))


@input_error
def days_to_bd(name: str):
    name = search_in(name)
    print(f'Number of days to the birthday of the {name} '
          f'is {contacts_new[name].days_to_birthday_() if contacts_new[name].days_to_birthday_() else None}.')


def print_instructions():
    print('''\n\tGeneral commands for all written contacts:
        To create a new contact enter: add contact <name of a new contact>
        To delete some contact enter: delete contact <name of a contact>
        To search a contact by a name or a phone or an email either a date of birth 
        using a full parameter/key of the field or only a part of it enter: search <key>
        To show all notices of an address book enter: show all

    General commands for each contact:
        To change a name of some contact enter: change name <name of contact>
        To add a new phone number to some contact enter: add phone <name of a contact>
        To change a phone number of some contact enter: change phone <name of a contact>
        To delete a phone number of some contact enter: delete phone <name os a contact>
        To change/add (if this field is empty) an email of some contact enter: change email <name of a contact>
        To change/add (if this field is empty) a date of birth of some contact enter: change bd <name of a contact>
        To show how many days left to someone birthday enter: days to bd <name of a contact>
        To read all commands once again enter: help
        To exit and shut down the CUI assistant enter: good bye or close or exit 

    All phone numbers should be added according to a phone pattern: +<code of a country>XXXXXXXXX or 0XXXXXXXXX
    All phone numbers are saved according to the pattern: +<code of a country>(XX)XXXXXXX
    Names, phone numbers, emails and other parameters have to be written without brackets <...>''')


def farewell():
    data_1 = get_info_from_class(contacts_new)
    with open('phone_numbers_1.json', 'w') as file:
        json.dump(data_1, file, cls=DateFormatEncoder, indent=4)
    print('Good bye!')
    sys.exit()


def greeting():
    print('Welcome to the CUI personal assistant.\n'
          'I can help you with adding, changing, showing and storing all contacts and data connected with them.')
    try:
        with open('phone_numbers_1.json', 'r') as f:  # write all data from a json file to a dict
            data_from_file = json.load(f, object_hook=as_date_datetime)
        [contacts_new.add_record(Record(name=key, phone=val['telephone number(-s)'], email=val['Email'],
                                        date_b=(val['Birthday'].year, val['Birthday'].month, val['Birthday'].day)
                                        if val['Birthday'] else ()))
         for key, val in data_from_file.items()]
    except (FileExistsError, FileNotFoundError):
        print('There are not records yet. Your addressbook is empty.')


# ----------------------------------------------------------------------------------------------------------------------
methods = {'add contact': add_cont, 'delete contact': delete_cont, 'search': search, 'show all': show_contacts,
           'change name': change_name, 'add phone': add_phone_num, 'change phone': change_phone_num,
           'delete phone': delete_phone_num, 'change email': change_email, 'change bd': change_date_bd,
           'days to bd': days_to_bd, 'help': print_instructions, ('good bye', 'close', 'exit'): farewell}


# ----------------------------------------------------------------------------------------------------------------------
@input_error
def parser_commands(command: str) -> tuple:
    for func in methods:
        if isinstance(func, str) and re.search(func, command, flags=re.I):
            return func, re.sub(func, '', command, flags=re.I).strip()
        else:
            for el in func:
                if re.search(command, el, flags=re.I):
                    return func, ''


"""res = [(func, re.sub(func, '', command, flags=re.I).strip()) if isinstance(func, str) and re.search(func, command,
           flags=re.I) else (func, '') if [el for el in func if re.search(command, el, flags=re.I)] else ('', '')
           for func in methods]
    res = [el for el in res if el != ('', '')]
    return res[0]"""


def handler(key_word: str | tuple):
    return methods[key_word]


def search_in(name: str) -> str:
    name_ = [el for el in list(contacts_new.data.keys()) if re.search(name, el, flags=re.I)]
    if len(name_) == 1:
        return name_[0]


def as_date_datetime(dct):  # from json format datetime objects to a dict
    if '__datetime__' in dct:
        return datetime.strptime(dct['value'], '%d/%m/%Y %H:%M:%S')
    if '__date__' in dct:
        return datetime.strptime(dct['value'], '%d/%m/%Y').date()
    return dct


@input_error
def get_info_from_class(obj: AddressBook):  # write all data to a dict
    data: dict = {}
    for rec in obj.values():
        data.update({rec.name.get: {'telephone number(-s)': [ph for ph in rec.phone], 'Email': rec.email.get,
                                    'Birthday': datetime(rec.birth_day.value.year, rec.birth_day.value.month,
                                                         rec.birth_day.value.day) if rec.birth_day.value else None}})
    return data
