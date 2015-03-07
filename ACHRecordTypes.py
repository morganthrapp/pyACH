__author__ = 'Morgan Thrapp'

import datetime
import re

from pyach.field_lengths import FILE_HEADER_LENGTHS, FILE_CONTROL_LENGTHS, BATCH_HEADER_LENGTHS, \
    BATCH_CONTROL_LENGTHS, ENTRY_LENGTHS, ADDENDA_LENGTHS

# Datetime formats
today_with_format = datetime.date.today().strftime('%y%m%d')
now_with_format = datetime.datetime.now().time().strftime('%H%M')
yesterday = datetime.datetime.now() - datetime.timedelta(1)
yesterday_with_format = yesterday.strftime('%y%m%d')


# Service class codes:
MIXED = '200'
CREDIT = '220'
DEBIT = '225'

# Addenda type codes:
POS = '02'
MTE = '02'
SHR = '02'
CCD = '05'
CTX = '05'
PPD = '05'
CHANGE = '98'
RETURN = '99'

# Transaction codes:
CHECK_DEPOSIT = '22'
PRE_CHECK_CREDIT = '23'
REMIT_CHECK_CREDIT = '24'
CHECK_DEBIT = '27'
PRE_CHECK_DEBIT = '28'
REMIT_CHECK_DEBIT = '29'
SAVINGS_DEPOSIT = '32'
PRE_SAVINGS_CREDIT = '33'
REMIT_SAVINGS_CREDIT = '34'
SAVINGS_DEBIT = '37'
PRE_SAVINGS_DEBIT = '38'
REMIT_SAVINGS_DEBIT = '39'

# Payment Type Codes
SINGLE_ENTRY = 'S'
RECURRING = 'R'

# Justify types
JUSTIFY_MODES = {'SR': lambda f, x: f.rjust(x), 'SL': lambda f, x: f.ljust(x), 'SRAZ': lambda f, x: f.rjust(x, '0')}
SHIFT_RIGHT = 'SR'
SHIFT_LEFT = 'SL'
SHIFT_RIGHT_ADD_ZERO = 'SRAZ'

# Alphanumeric check
is_alphanumeric = re.compile('[\W_]+')


def validate_field(field, length, justify=None, to_alphanumeric=True):
    if to_alphanumeric:
        field = is_alphanumeric.sub('', field)
    if len(field.strip()) == 0:
        return ' ' * length
    elif len(field) == length:
        return field
    elif len(field) > length:
        return field[:length]
    elif justify in JUSTIFY_MODES:
        return JUSTIFY_MODES[justify](field, length)
    elif len(field) < length:
        return field[:length]


class FileHeader:
    _record_type = '1'  # ACH Header records are type 1
    _priority_code = '01'  # 01 is the only code supported by NACHA
    _record_size = '094'
    _blocking_factor = '10'
    _format_code = '1'

    def __init__(self, destination_routing_number,
                 company_identification_number, destination_name, origin_name,
                 reference_code):
        self._destination_routing_number = str(destination_routing_number)
        self._company_identification_number = str(company_identification_number)
        self._destination_name = str(destination_name)
        self._origin_name = str(origin_name)
        self._reference_code = str(reference_code)
        self._creation_date = today_with_format
        self._creation_time = now_with_format
        self._file_id_modifier = 'A'  # First file of the day has A. Subsequent files follow pattern A-Z/1-9
        self.file_header_record = ''

    def generate(self):
        self.file_header_record += validate_field(self._record_type, FILE_HEADER_LENGTHS['RECORD TYPE CODE'])
        self.file_header_record += validate_field(self._priority_code, FILE_HEADER_LENGTHS['PRIORITY CODE'])
        self.file_header_record += validate_field(self._destination_routing_number,
                                                  FILE_HEADER_LENGTHS['IMMEDIATE DESTINATION'], SHIFT_LEFT)
        self.file_header_record += validate_field(self._company_identification_number,
                                                  FILE_HEADER_LENGTHS['IMMEDIATE ORIGIN'], SHIFT_LEFT)
        self.file_header_record += validate_field(self._creation_date, FILE_HEADER_LENGTHS['FILE CREATION DATE'])
        self.file_header_record += validate_field(self._creation_time, FILE_HEADER_LENGTHS['FILE CREATION TIME'])
        self.file_header_record += validate_field(self._file_id_modifier, FILE_HEADER_LENGTHS['FILE ID MODIFIER'])
        self.file_header_record += validate_field(self._record_size, FILE_HEADER_LENGTHS['RECORD SIZE'])
        self.file_header_record += validate_field(self._blocking_factor, FILE_HEADER_LENGTHS['BLOCKING FACTOR'])
        self.file_header_record += validate_field(self._format_code, FILE_HEADER_LENGTHS['FORMAT CODE'])
        self.file_header_record += validate_field(self._destination_name,
                                                  FILE_HEADER_LENGTHS['IMMEDIATE DESTINATION NAME'], SHIFT_LEFT)
        self.file_header_record += validate_field(self._origin_name, FILE_HEADER_LENGTHS['IMMEDIATE ORIGIN NAME'],
                                                  SHIFT_LEFT)
        self.file_header_record += validate_field(self._reference_code, FILE_HEADER_LENGTHS['REFERENCE CODE'],
                                                  SHIFT_LEFT)
        self.file_header_record += '\n'
        self._file_id_modifier = chr(ord(self._file_id_modifier) + 1)
        return self.file_header_record


class FileControl:
    _record_type = '9'  # ACH File Control records are type 9
    __reserved = ''  # DO NOT MODIFY THIS. It needs to be blank.

    def __init__(self, batch_count, block_count, entry_count, entry_hash,
                 total_debt_amount, total_credit_amount):
        self._batch_count = str(batch_count)
        self._block_count = str(block_count)
        self._entry_count = str(entry_count)
        self._entry_hash = str(entry_hash)
        self._total_debit_amount = total_debt_amount
        self._total_credit_amount = total_credit_amount
        self.file_control_record = ''

    def generate(self):
        self.file_control_record += validate_field(self._record_type, FILE_CONTROL_LENGTHS['RECORD TYPE CODE'])
        self.file_control_record += validate_field(self._batch_count, FILE_CONTROL_LENGTHS['BATCH COUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.file_control_record += validate_field(self._block_count, FILE_CONTROL_LENGTHS['BLOCK COUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.file_control_record += validate_field(self._entry_count, FILE_CONTROL_LENGTHS['DETAIL COUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.file_control_record += validate_field(self._entry_hash, FILE_CONTROL_LENGTHS['ENTRY HASH'], SHIFT_LEFT)
        self.file_control_record += validate_field(str(self._total_debit_amount),
                                                   FILE_CONTROL_LENGTHS['TOTAL DEBIT AMOUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO, True)
        self.file_control_record += validate_field(str(self._total_credit_amount),
                                                   FILE_CONTROL_LENGTHS['TOTAL CREDIT AMOUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO, True)
        self.file_control_record += validate_field(self.__reserved, FILE_CONTROL_LENGTHS['RESERVED'], SHIFT_LEFT)

        return self.file_control_record


class Batch:
    def __init__(self, company_identification_number,
                 dfi_number, service_class):
        self._company_identification_number = company_identification_number
        self._originator_dfi_identification = dfi_number
        self._service_class = service_class
        self._company_name = ''
        self._batch_header = ''
        self._total_debit_amount = 0
        self._total_credit_amount = 0
        self._entry_hash = 0
        self._entry_count = 0
        self.entry_records = []

    def add_entry(self, transaction_code, routing_number, account_number,
                  amount, identification_number, receiver_name,
                  discretionary_data=''):
        _entry = Entry(transaction_code, routing_number, account_number,
                       amount, identification_number, receiver_name,
                       discretionary_data, self._originator_dfi_identification)
        self.entry_records.append(_entry)

    def finalize(self, company_name, discretionary_data, entry_class_code,
                 entry_description, batch_number,
                 service_class=MIXED, description_date=today_with_format,
                 effective_entry_date=today_with_format):
        self._batch_header = BatchHeader(company_name, discretionary_data,
                                         self._company_identification_number,
                                         entry_class_code, entry_description,
                                         self._originator_dfi_identification,
                                         batch_number, service_class,
                                         description_date,
                                         effective_entry_date)
        for entry in self.entry_records:
            self._batch_header.entry_records.append(entry)
        self._batch_header.finalize()
        self._total_debit_amount = self._batch_header._total_debit_amount
        self._total_credit_amount = self._batch_header._total_credit_amount
        self._entry_hash = self._batch_header._entry_hash
        self._entry_count = self._batch_header._entry_count


class BatchHeader:
    _record_type = '5'  # ACH Batch Header records are type 5
    __reserved = ' '  # DO NOT MODIFY THIS.
    # It is auto generated by the receiving bank.
    _originator_status_code = '1'

    def __init__(self, company_name, discretionary_data,
                 company_identification_number,
                 entry_class_code, entry_description, dfi_number, batch_number,
                 service_class=MIXED, description_date=today_with_format,
                 effective_entry_date=today_with_format):
        self._company_name = str(company_name)
        self._discretionary_data = str(discretionary_data)
        self._company_identification_number = str(company_identification_number)
        self._entry_class_code = str(entry_class_code)
        self._service_class = str(service_class)
        self._entry_description = str(entry_description)
        self._descriptive_date = str(description_date)
        self._effective_entry_date = str(effective_entry_date)
        self._originator_dfi_identification = str(dfi_number)
        self._batch_number = str(batch_number)
        self._batch_control_record = ''
        self.entry_records = []
        self._entry_count = 0
        self._total_debit_amount = 0
        self._total_credit_amount = 0
        self._entry_hash = 0
        self.batch_header_record = ''

    def generate(self):
        self.batch_header_record += validate_field(self._record_type, BATCH_HEADER_LENGTHS['RECORD TYPE CODE'])
        self.batch_header_record += validate_field(self._service_class, BATCH_HEADER_LENGTHS['SERVICE CLASS CODE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self._company_name, BATCH_HEADER_LENGTHS['COMPANY NAME'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self._discretionary_data, BATCH_HEADER_LENGTHS['DISCRETIONARY DATA'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self._company_identification_number,
                                                   BATCH_HEADER_LENGTHS['COMPANY IDENTIFICATION'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self._entry_class_code, BATCH_HEADER_LENGTHS['ENTRY CLASS CODE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self._entry_description, BATCH_HEADER_LENGTHS['ENTRY DESCRIPTION'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self._descriptive_date, BATCH_HEADER_LENGTHS['DESCRIPTIVE DATE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self._effective_entry_date,
                                                   BATCH_HEADER_LENGTHS['EFFECTIVE ENTRY DATE'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self.__reserved, BATCH_HEADER_LENGTHS['SETTLEMENT DATE'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self._originator_status_code,
                                                   BATCH_HEADER_LENGTHS['ORIGINATOR STATUS CODE'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self._originator_dfi_identification,
                                                   BATCH_HEADER_LENGTHS['ORIGINATING DFI IDENTIFICATION'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self._batch_number, BATCH_HEADER_LENGTHS['BATCH NUMBER'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.batch_header_record += '\n'
        return self.batch_header_record

    def finalize(self):
        entry_hash = 0
        for entry in self.entry_records:
            entry.finalize()
            self._entry_count += 1
            if entry._transaction_code in (CHECK_DEBIT, SAVINGS_DEBIT):
                self._total_debit_amount += entry._amount
            elif entry._transaction_code in (CHECK_DEPOSIT, SAVINGS_DEPOSIT):
                self._total_credit_amount += entry._amount
            entry_hash += int(entry._routing_number)
        self._entry_hash = str(entry_hash)[-10:]
        self._batch_control_record = BatchControl(self._entry_count,
                                                  self._entry_hash,
                                                  self._total_debit_amount,
                                                  self._total_credit_amount,
                                                  self._company_identification_number,
                                                  self._originator_dfi_identification,
                                                  self._batch_number,
                                                  self._service_class).generate()

    def add_entry(self, transaction_code, routing_number, account_number,
                  amount, identification_number, receiver_name,
                  discretionary_data=''):
        _entry = Entry(transaction_code, routing_number, account_number,
                       amount, identification_number, receiver_name,
                       discretionary_data, self._originator_dfi_identification)
        self.entry_records.append(_entry)


class BatchControl:
    _record_type = '8'  # ACH Batch Control records are type 8
    __authentication_code = ''  # DO NOT MODIFY THIS. It needs to be blank.
    __reserved = ''  # DO NOT MODIFY THIS. It needs to be blank.

    def __init__(self, entry_count, entry_hash, total_debt_amount,
                 total_credit_amount, company_identification_number,
                 dfi_number, batch_number, service_class=MIXED):
        self._service_class = str(service_class)
        self._entry_count = str(entry_count)
        self.entry_hash = str(entry_hash)
        self._total_debit_amount = total_debt_amount
        self._total_credit_amount = total_credit_amount
        self._company_identification_number = str(company_identification_number)
        self._originator_dfi_identification = str(dfi_number)
        self._batch_number = str(batch_number)
        self.batch_control_record = ''

    def generate(self):
        self.batch_control_record += validate_field(self._record_type, BATCH_CONTROL_LENGTHS['RECORD TYPE CODE'])
        self.batch_control_record += validate_field(self._service_class, BATCH_CONTROL_LENGTHS['SERVICE CLASS CODE'],
                                                    SHIFT_LEFT)
        self.batch_control_record += validate_field(self._entry_count, BATCH_CONTROL_LENGTHS['DETAIL COUNT'],
                                                    SHIFT_RIGHT_ADD_ZERO)
        self.batch_control_record += validate_field(self.entry_hash, BATCH_CONTROL_LENGTHS['ENTRY HASH'], SHIFT_LEFT)
        self.batch_control_record += validate_field(str(self._total_debit_amount),
                                                    BATCH_CONTROL_LENGTHS['TOTAL DEBIT AMOUNT'],
                                                    SHIFT_RIGHT_ADD_ZERO, True)
        self.batch_control_record += validate_field(str(self._total_credit_amount),
                                                    BATCH_CONTROL_LENGTHS['TOTAL CREDIT AMOUNT'],
                                                    SHIFT_RIGHT_ADD_ZERO, True)
        self.batch_control_record += validate_field(self._company_identification_number,
                                                    BATCH_CONTROL_LENGTHS['COMPANY IDENTIFICATION'],
                                                    SHIFT_RIGHT_ADD_ZERO)
        self.batch_control_record += validate_field(self.__authentication_code,
                                                    BATCH_CONTROL_LENGTHS['AUTHENTICATION CODE'], SHIFT_LEFT)
        self.batch_control_record += validate_field(self.__reserved, BATCH_CONTROL_LENGTHS['RESERVED'], SHIFT_LEFT)
        self.batch_control_record += validate_field(self._originator_dfi_identification,
                                                    BATCH_CONTROL_LENGTHS['ORIGINATING DFI IDENTIFICATION'], SHIFT_LEFT)
        self.batch_control_record += validate_field(self._batch_number, BATCH_CONTROL_LENGTHS['BATCH NUMBER'],
                                                    SHIFT_RIGHT_ADD_ZERO)
        self.batch_control_record += '\n'
        return self.batch_control_record


class Entry:
    _entry_number = 0
    # The following values are printed:
    _record_type = '6'  # Entry Detail record type is 6.

    def __init__(self, transaction_code, routing_number, account_number,
                 amount, identification_number, receiver_name,
                 discretionary_data, trace_number):
        self._transaction_code = str(transaction_code)
        self._routing_number = routing_number
        self._account_number = str(account_number)
        self._amount = amount
        self._identification_number = str(identification_number)
        self._receiver_name = str(receiver_name)
        self._discretionary_data = str(discretionary_data)
        self._trace_number = str(trace_number)
        self._addenda_count = 0
        self.entry_record = ''
        self.addenda_records = []
        self._has_addenda = '0'
        self._entry_number += 1

    def _get_trace_number(self):
        trace_number = '{0}{1}'.format(self._trace_number, str(self._entry_number).ljust(7, '0'))
        return trace_number

    def _check_digit(self):
        routing_number_list = list(self._routing_number)
        routing_number_sum = 0
        routing_number_sum += (int(routing_number_list[0]) * 3)
        routing_number_sum += (int(routing_number_list[1]) * 7)
        routing_number_sum += (int(routing_number_list[2]))
        routing_number_sum += (int(routing_number_list[3]) * 3)
        routing_number_sum += (int(routing_number_list[4]) * 7)
        routing_number_sum += (int(routing_number_list[5]))
        routing_number_sum += (int(routing_number_list[6]) * 3)
        routing_number_sum += (int(routing_number_list[7]) * 7)
        check_digit = 10 - (routing_number_sum % 10)
        return str(check_digit)

    def generate(self):
        self.entry_record += validate_field(self._record_type, ENTRY_LENGTHS['RECORD TYPE CODE'])
        self.entry_record += validate_field(self._transaction_code, ENTRY_LENGTHS['TRANSACTION CODE'], SHIFT_LEFT)
        self.entry_record += validate_field(self._routing_number, ENTRY_LENGTHS['RECEIVING DFI ID'], SHIFT_LEFT)
        self.entry_record += validate_field(self._check_digit(), ENTRY_LENGTHS['CHECK DIGIT'], SHIFT_LEFT)
        self.entry_record += validate_field(self._account_number, ENTRY_LENGTHS['DFI ACCOUNT NUMBER'], SHIFT_LEFT)
        self.entry_record += validate_field(str(self._amount), ENTRY_LENGTHS['DOLLAR AMOUNT'],
                                            SHIFT_RIGHT_ADD_ZERO, True)
        self.entry_record += validate_field(self._identification_number, ENTRY_LENGTHS['INDIVIDUAL IDENTIFICATION'],
                                            SHIFT_LEFT)
        self.entry_record += validate_field(self._receiver_name, ENTRY_LENGTHS['INDIVIDUAL NAME'], SHIFT_LEFT)
        self.entry_record += validate_field(self._discretionary_data, ENTRY_LENGTHS['DISCRETIONARY DATA'], SHIFT_LEFT)
        self.entry_record += validate_field(self._has_addenda, ENTRY_LENGTHS['ADDENDA'], SHIFT_LEFT)
        self.entry_record += validate_field(self._get_trace_number(), ENTRY_LENGTHS['TRACE NUMBER'], SHIFT_LEFT)
        self.entry_record += '\n'
        return self.entry_record[:95]

    def finalize(self):
        self._addenda_count = len(self.addenda_records)

    def add_addenda(self, main_detail, type_code):
        _entry_record_id = str(self._trace_number)
        _addenda_record = Addenda(main_detail, type_code, _entry_record_id)
        self.addenda_records.append(_addenda_record)
        self._has_addenda = '1'


class Addenda:
    _record_type = '7'  # Addenda records are type 7

    def __init__(self, main_detail, type_code, entry_record_id):
        self._main_detail = str(main_detail)
        self._type_code = str(type_code)
        self._entry_record_id = str(entry_record_id)
        self._addenda_sequence = 1
        self.addenda_record = ''

    def generate(self):
        self.addenda_record += validate_field(self._record_type, ADDENDA_LENGTHS['RECORD TYPE'])
        self.addenda_record += validate_field(self._type_code, ADDENDA_LENGTHS['TYPE CODE'], SHIFT_LEFT)
        self.addenda_record += validate_field(self._main_detail, ADDENDA_LENGTHS['MAIN DETAIL'], SHIFT_LEFT)
        self.addenda_record += validate_field(str(self._addenda_sequence), ADDENDA_LENGTHS['SEQUENCE'], SHIFT_LEFT)
        self.addenda_record += validate_field(self._entry_record_id, ADDENDA_LENGTHS['ENTRY RECORD ID'], SHIFT_LEFT)
        self.addenda_record += '\n'
        self._addenda_sequence += 1
        return self.addenda_record


class ACHFile(object):
    def __init__(self):
        self._batch_count = 0
        self._batch_number = 0
        self._block_count = 0
        self._entry_count = 0
        self._entry_addenda_count = 0
        self._entry_hash = ''
        self._total_debit_amount = 0
        self._total_credit_amount = 0
        self._entry_date = today_with_format
        self._file_header = ''
        self._file_control_record = ''
        self.batch_records = []
        self.destination_name = ''
        self.origin_name = ''
        self.reference_code = ''
        self.header_discretionary_data = ''
        self.entry_class_code = ''
        self.entry_description = ''
        self.descriptive_date = today_with_format
        self.destination_routing_number = ''
        self.company_identification_number = ''
        self.footer_lines = 0
        self.origin_id = ''

    def create_header(self):
        self._file_header = FileHeader(self.destination_routing_number,
                                       self.origin_id,
                                       self.destination_name,
                                       self.origin_name,
                                       self.reference_code)

    def new_batch(self, dfi_number, batch_name, entry_description=None,
                  company_identification_number=None,
                  entry_class_code=None, discretionary_data='',
                  service_class=MIXED):
        if entry_description is None:
            entry_description = self.entry_description
        if company_identification_number is None:
            company_identification_number = self.company_identification_number
        if entry_class_code is None:
            entry_class_code = self.entry_class_code
        self._batch_number += 1
        new_batch = BatchHeader(batch_name, discretionary_data,
                                company_identification_number,
                                entry_class_code, entry_description,
                                dfi_number, self._batch_number, service_class,
                                self.descriptive_date)
        self.batch_records.append(new_batch)

    def append_batch(self, batch):
        self.batch_records.append(batch)

    def save(self, file_path):
        self._batch_count = self._batch_number
        self._block_count = 2 + self.footer_lines
        self._entry_count = 0
        self._total_debit_amount = 0
        self._total_credit_amount = 0
        entry_hash = 0
        for batch in self.batch_records:
            batch.finalize()
            self._block_count += int(batch._entry_count) + 2
            self._entry_count += int(batch._entry_count)
            self._total_debit_amount += batch._total_debit_amount
            self._total_credit_amount += batch._total_credit_amount
            entry_hash += int(batch._entry_hash)
        self._entry_hash = str(entry_hash)[-10:]
        self._file_control_record = FileControl(self._batch_count, self._block_count,
                                                self._entry_count, self._entry_hash,
                                                self._total_debit_amount, self._total_credit_amount)
        with open(file_path, 'w+') as ach_file:
            file_header = self._file_header.generate()
            ach_file.write(file_header)
            for batch in self.batch_records:
                batch_header = batch.generate()
                ach_file.write(batch_header)
                for entry in batch.entry_records:
                    entry_record = entry.generate()
                    ach_file.write(entry_record)
                    for addenda in entry.addenda_records:
                        addenda_record = addenda.generate()
                        ach_file.write(addenda_record)
                batch_control = batch._batch_control_record
                ach_file.write(batch_control)
            file_control_record = self._file_control_record.generate()
            ach_file.write(file_control_record)

            if self.footer_lines > 0:
                line = '\n'.ljust(95, '9')
                for x in range(0, self.footer_lines):
                    ach_file.write(line)
