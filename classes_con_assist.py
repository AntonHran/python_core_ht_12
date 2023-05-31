from collections import UserDict, UserList
from datetime import datetime, date
import re
import json
from const import european_codes, ukr_mobile_phone_codes


class Field:
    def __init__(self, value):
        self.value = value
        # self.__value = None

    def set_value(self, val):
        if val:
            self.value = val

    @property
    def get(self):
        return self.value


class Name(Field):
    pass


class Phone(Field, UserList):
    def __init__(self, value: str | int | list):
        Field.__init__(self, value)
        UserList.__init__(self)
        self.value = None
        self.check(value)

    def check_number(self, number):
        try:
            if number:
                number = ''.join([re.sub('[+\-() ]', '', symbol) for symbol in str(number)])
                if re.match(r'^([0-9]){6,14}[0-9]$', number):
                    for code in european_codes:
                        if number.startswith(code):
                            number = number[len(code):]
                            self.value = f'+{code}({number[:2]}){number[2:]}'
                            return f'+{code}({number[:2]}){number[2:]}'
                    else:
                        for inner_code in ukr_mobile_phone_codes:
                            if number.startswith(inner_code) and len(number) == 10:
                                number = number[1:]
                                self.value = f'+380({number[:2]}){number[2:]}'
                                return f'+380({number[:2]}){number[2:]}'
                else:
                    print('All phone numbers should be added according to a phone pattern: '
                          '+code of a countryXXXXXXXXX or 0XXXXXXXXX')
        except (ValueError, IndexError) as error:
            print(error)

    def check(self, phones: str | int | list):
        if isinstance(phones, list):
            [self.add_phone_num(phone) for phone in phones]
        else:
            self.add_phone_num(phones)

    @property
    def get(self):
        return self.data

    def add_phone_num(self, phone_num):
        res = self.check_number(phone_num)
        if self.value and res:
            self.data.append(self.value)


class Email(Field):
    def set_value(self, val):
        if re.match(r"([a-zA-Z.]+\w+\.?)+(@\w{2,}\.)(\w{2,})", val):
            self.value = val
        else:
            self.value = None
            raise ValueError
    '''def get(self):
        return self.value'''


class Birthday(Field):
    def __init__(self, date_: tuple):
        super().__init__(date_)
        self.value = None
        self.check_date(date_)

    def check_date(self, date_b: tuple):
        try:
            if date_b:
                year, month, day = int(date_b[0]), int(date_b[1]), int(date_b[2])
                if year in range(1900, date.today().year + 1) and month in range(1, 13) and day in range(1, 32):
                    self.value = date(year=date_b[0], month=date_b[1], day=date_b[2])  # date(*date_b)
                else:
                    raise ValueError
        except (TypeError, ValueError, IndexError):
            print('A date of the birth has to be written according to a birthday pattern: YYYY, MM, DD')


class Record:
    def __init__(self, name: str, phone: str | int | list = None, email: str = None, date_b: tuple = ()):
        self.name = Name(name)
        self.phone = Phone(phone)
        self.email = Email(email)
        self.birth_day = Birthday(date_b)

    def add_number(self, phone: str | int):
        self.phone.add_phone_num(phone)

    def delete_number(self, phone_num):
        self.phone.remove(phone_num)

    def change_number(self, old_phone_num, changed_phone_num):
        ind = self.phone.index(old_phone_num)
        self.phone.remove(old_phone_num)
        self.phone.insert(ind, changed_phone_num)

    def add_change_email(self, email_val):
        self.email = Email(email_val)
        self.email.set_value(email_val)

    def add_bd(self, date_c: tuple):
        self.birth_day = Birthday(date_c)

    def days_to_birthday_(self):
        if self.birth_day.value:
            current_date: date = date.today()
            birthday: date = date(year=current_date.year, month=self.birth_day.value.month,
                                  day=self.birth_day.value.day)
            diff: int = (birthday - current_date).days
            if diff < 0:
                birthday = date(year=current_date.year + 1, month=self.birth_day.value.month,
                                day=self.birth_day.value.day)
                diff = (birthday - current_date).days
            return diff

    '''def days_to_birthday__(self):
        if self.birth_day.value:
            return (datetime(year=datetime.now().year + 1, month=self.birth_day.value.month,
                             day=self.birth_day.value.day) - datetime.now()).days \
                if (datetime(year=datetime.now().year, month=self.birth_day.value.month,
                             day=self.birth_day.value.day) - datetime.now()).days < 0 \
                else (datetime(year=datetime.now().year, month=self.birth_day.value.month,
                               day=self.birth_day.value.day) - datetime.now()).days'''


class AddressBook(UserDict):
    N: int = 2

    def add_record(self, record):
        self.data[record.name.get] = record

    def change_name(self, old_name, new_name):
        contact_data = self.data[old_name]
        del self.data[old_name]
        contact_data.name.set_value(new_name)
        self.data[contact_data.name.value] = contact_data

    def delete_record(self, name: str):
        del self.data[name]

    def __str__(self):
        return [print(f'Name: {name} -> Info: telephone number(-s): {rec.phone} | Email: {rec.email.get} '
                      f'| Birthday: {rec.birth_day.get}.') for name, rec in self.data.items()]

    def iterator(self):
        start = 0
        end = self.N
        while True:
            data = list(self.data.keys())[start:end]
            if not data:
                break
            yield {name: f'Info: telephone number(-s): {self.data[name].phone} | Email: {self.data[name].email.get} '
                         f'| Birthday: {self.data[name].birth_day.get}.' for name in data}
            start = end
            end += self.N

    def search(self, parameter: str | int):
        try:
            match_ = [rec.name.get for rec in self.data.values() if re.search(parameter, rec.name.get, flags=re.I) or
                      [num for num in rec.phone if re.search(parameter, num)]
                      or re.search(parameter, rec.email.get if rec.email.get else '', flags=re.I) or
                      (rec.birth_day.get and (re.search(parameter, str(rec.birth_day.value.year)) or
                                              re.search(parameter, str(rec.birth_day.value.month)) or re.search(
                                  parameter, str(rec.birth_day.value.day))))]

            [print(f'Name: {self.data[el].name.get} -> Info: telephone number(-s): {self.data[el].phone} | '
                   f'Email: {self.data[el].email.get} | Birthday: {self.data[el].birth_day.get}.') for el in match_] \
                if match_ else print('There are not matches.')
        except (AttributeError, KeyError, ValueError, TypeError) as e:
            print(e)


class DateFormatEncoder(json.JSONEncoder):  # write datetime objects to json

    def default(self, obj):
        if isinstance(obj, datetime):
            return {'value': obj.strftime('%d/%m/%Y %H:%M:%S'), '__datetime__': True}
        elif isinstance(obj, date):
            return {'value': obj.strftime('%d/%m/%Y'), '__date__': True}
        return json.JSONEncoder.default(self, obj)


contacts_new = AddressBook()
