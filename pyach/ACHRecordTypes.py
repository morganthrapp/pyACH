import datetime
import re
import os.path

import decimal
import holidays
import pyach.field_lengths as field_lengths

# Datetime formats
day_format_string = r'%y%m%d'
today_with_format = datetime.date.today().strftime(day_format_string)
now_with_format = datetime.datetime.now().time().strftime('%H%M')
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday_with_format = yesterday.strftime(day_format_string)
tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
tomorrow_with_format = tomorrow.strftime(day_format_string)
WEEKEND = [6, 7]
HOLIDAYS = holidays.US()

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

decimal.getcontext().prec = 10


def validate_field(field, length, justify=None, to_alphanumeric=True):
    if to_alphanumeric:
        field = is_alphanumeric.sub('', field)
    if not field.strip():
        return ' ' * length
    elif len(field) > length:
        return field[:length]
    elif justify in JUSTIFY_MODES:
        return JUSTIFY_MODES[justify](field, length)
    else:
        return field


def next_valid_effective_entry_date(_date=None):
    if _date is None:
        _date = datetime.datetime.today()
    while (_date.isoweekday() in WEEKEND) or (_date.date() in HOLIDAYS):
        _date += datetime.timedelta(days=1)
    return _date


def get_effective_entry_date(effective_entry_date, as_date=False):
    _date = next_valid_effective_entry_date()
    if effective_entry_date > 0:
        # We have to delay for at least one day
        if effective_entry_date < 2 and _date.isoweekday() in WEEKEND + [5]:
            effective_entry_date = 2
        for _ in range(effective_entry_date if effective_entry_date > 0 else 1):
            _date += datetime.timedelta(days=1)
            _date = next_valid_effective_entry_date(_date)
    if as_date:
        return _date
    else:
        return _date.strftime(day_format_string)


class IDStore:
    def __init__(self):
        self.id = 0

    def get_id(self):
        self.id += 1
        return self.id


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
        self.file_header_record += validate_field(self._record_type,
                                                  field_lengths.FILE_HEADER_LENGTHS['RECORD TYPE CODE'])
        self.file_header_record += validate_field(self._priority_code,
                                                  field_lengths.FILE_HEADER_LENGTHS['PRIORITY CODE'])
        self.file_header_record += validate_field(self._destination_routing_number,
                                                  field_lengths.FILE_HEADER_LENGTHS['IMMEDIATE DESTINATION'],
                                                  SHIFT_RIGHT)
        self.file_header_record += validate_field(self._company_identification_number,
                                                  field_lengths.FILE_HEADER_LENGTHS['IMMEDIATE ORIGIN'], SHIFT_LEFT)
        self.file_header_record += validate_field(self._creation_date,
                                                  field_lengths.FILE_HEADER_LENGTHS['FILE CREATION DATE'])
        self.file_header_record += validate_field(self._creation_time,
                                                  field_lengths.FILE_HEADER_LENGTHS['FILE CREATION TIME'])
        self.file_header_record += validate_field(self._file_id_modifier,
                                                  field_lengths.FILE_HEADER_LENGTHS['FILE ID MODIFIER'])
        self.file_header_record += validate_field(self._record_size, field_lengths.FILE_HEADER_LENGTHS['RECORD SIZE'])
        self.file_header_record += validate_field(self._blocking_factor,
                                                  field_lengths.FILE_HEADER_LENGTHS['BLOCKING FACTOR'])
        self.file_header_record += validate_field(self._format_code, field_lengths.FILE_HEADER_LENGTHS['FORMAT CODE'])
        self.file_header_record += validate_field(self._destination_name,
                                                  field_lengths.FILE_HEADER_LENGTHS['IMMEDIATE DESTINATION NAME'],
                                                  SHIFT_LEFT)
        self.file_header_record += validate_field(self._origin_name,
                                                  field_lengths.FILE_HEADER_LENGTHS['IMMEDIATE ORIGIN NAME'],
                                                  SHIFT_LEFT)
        self.file_header_record += validate_field(self._reference_code,
                                                  field_lengths.FILE_HEADER_LENGTHS['REFERENCE CODE'],
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
        self.file_control_record += validate_field(self._record_type,
                                                   field_lengths.FILE_CONTROL_LENGTHS['RECORD TYPE CODE'])
        self.file_control_record += validate_field(self._batch_count, field_lengths.FILE_CONTROL_LENGTHS['BATCH COUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.file_control_record += validate_field(self._block_count, field_lengths.FILE_CONTROL_LENGTHS['BLOCK COUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.file_control_record += validate_field(self._entry_count,
                                                   field_lengths.FILE_CONTROL_LENGTHS['DETAIL COUNT'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.file_control_record += validate_field(self._entry_hash, field_lengths.FILE_CONTROL_LENGTHS['ENTRY HASH'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.file_control_record += validate_field(
            str(self._total_debit_amount.quantize(decimal.Decimal('.01'))),
            field_lengths.FILE_CONTROL_LENGTHS['TOTAL DEBIT AMOUNT'], SHIFT_RIGHT_ADD_ZERO, True)
        self.file_control_record += validate_field(
            str(self._total_credit_amount.quantize(decimal.Decimal('.01'))),
            field_lengths.FILE_CONTROL_LENGTHS['TOTAL CREDIT AMOUNT'], SHIFT_RIGHT_ADD_ZERO, True)
        self.file_control_record += validate_field(self.__reserved, field_lengths.FILE_CONTROL_LENGTHS['RESERVED'],
                                                   SHIFT_LEFT)

        return self.file_control_record


class BatchHeader:
    _record_type = '5'  # ACH Batch Header records are type 5
    __reserved = ' '  # DO NOT MODIFY THIS.
    # It is auto generated by the receiving bank.
    _originator_status_code = '1'

    def __init__(self, company_name, discretionary_data,
                 company_identification_number,
                 entry_class_code, entry_description, dfi_number, batch_number, id_store,
                 service_class=MIXED, description_date=today_with_format,
                 effective_entry_delay=1):
        self.batch_control_record = None
        self.company_name = str(company_name)
        self.discretionary_data = str(discretionary_data)
        self.company_identification_number = str(company_identification_number)
        self.entry_class_code = str(entry_class_code)
        self.service_class = str(service_class)
        self.entry_description = str(entry_description)
        self.descriptive_date = str(description_date)
        self.effective_entry_date = get_effective_entry_date(effective_entry_delay)
        self.originator_dfi_identification = str(dfi_number)
        self.batch_number = str(batch_number)
        self.batch_control_record = ''
        self.entry_records = []
        self.batch_header_record = ''
        self._id_store = id_store

    @property
    def total_debit_amount(self):
        return decimal.Decimal(sum(
            entry.amount for entry in self.entry_records if entry.transaction_code in (CHECK_DEBIT, SAVINGS_DEBIT)))

    @property
    def total_credit_amount(self):
        return decimal.Decimal(sum(
            entry.amount for entry in self.entry_records if entry.transaction_code in (CHECK_DEPOSIT, SAVINGS_DEPOSIT)))

    @property
    def entry_hash(self):
        return sum(int(str(entry.routing_number)[:8]) for entry in self.entry_records)

    @property
    def entry_count(self):
        return len(self.entry_records) + sum(entry.addenda_count for entry in self.entry_records)

    def generate(self):
        self.batch_header_record += validate_field(self._record_type,
                                                   field_lengths.BATCH_HEADER_LENGTHS['RECORD TYPE CODE'])
        self.batch_header_record += validate_field(self.service_class,
                                                   field_lengths.BATCH_HEADER_LENGTHS['SERVICE CLASS CODE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.company_name,
                                                   field_lengths.BATCH_HEADER_LENGTHS['COMPANY NAME'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self.discretionary_data,
                                                   field_lengths.BATCH_HEADER_LENGTHS['DISCRETIONARY DATA'],
                                                   SHIFT_LEFT, to_alphanumeric=False)
        self.batch_header_record += validate_field(self.company_identification_number,
                                                   field_lengths.BATCH_HEADER_LENGTHS['COMPANY IDENTIFICATION'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.entry_class_code,
                                                   field_lengths.BATCH_HEADER_LENGTHS['ENTRY CLASS CODE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.entry_description,
                                                   field_lengths.BATCH_HEADER_LENGTHS['ENTRY DESCRIPTION'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.descriptive_date,
                                                   field_lengths.BATCH_HEADER_LENGTHS['DESCRIPTIVE DATE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.effective_entry_date,
                                                   field_lengths.BATCH_HEADER_LENGTHS['EFFECTIVE ENTRY DATE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.__reserved,
                                                   field_lengths.BATCH_HEADER_LENGTHS['SETTLEMENT DATE'], SHIFT_LEFT)
        self.batch_header_record += validate_field(self._originator_status_code,
                                                   field_lengths.BATCH_HEADER_LENGTHS['ORIGINATOR STATUS CODE'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.originator_dfi_identification,
                                                   field_lengths.BATCH_HEADER_LENGTHS['ORIGINATING DFI IDENTIFICATION'],
                                                   SHIFT_LEFT)
        self.batch_header_record += validate_field(self.batch_number,
                                                   field_lengths.BATCH_HEADER_LENGTHS['BATCH NUMBER'],
                                                   SHIFT_RIGHT_ADD_ZERO)
        self.batch_header_record += '\n'
        return self.batch_header_record

    def finalize(self):
        self.batch_control_record = BatchControl(self.entry_count,
                                                 self.entry_hash,
                                                 self.total_debit_amount,
                                                 self.total_credit_amount,
                                                 self.company_identification_number,
                                                 self.originator_dfi_identification,
                                                 self.batch_number,
                                                 self.service_class).generate()

    def add_entry(self, transaction_code, routing_number, account_number,
                  amount, identification_number, receiver_name, discretionary_data=''):
        _entry = Entry(transaction_code, routing_number, account_number,
                       amount, identification_number, receiver_name,
                       discretionary_data, self.originator_dfi_identification, self._id_store.get_id())
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
        self._entry_hash = str(entry_hash)[-10:]
        self._total_debit_amount = total_debt_amount
        self._total_credit_amount = total_credit_amount
        self._company_identification_number = str(company_identification_number)
        self._originator_dfi_identification = str(dfi_number)
        self._batch_number = str(batch_number)
        self.batch_control_record = ''

    def generate(self):
        self.batch_control_record += validate_field(self._record_type,
                                                    field_lengths.BATCH_CONTROL_LENGTHS['RECORD TYPE CODE'])
        self.batch_control_record += validate_field(self._service_class,
                                                    field_lengths.BATCH_CONTROL_LENGTHS['SERVICE CLASS CODE'],
                                                    SHIFT_LEFT)
        self.batch_control_record += validate_field(self._entry_count,
                                                    field_lengths.BATCH_CONTROL_LENGTHS['DETAIL COUNT'],
                                                    SHIFT_RIGHT_ADD_ZERO)
        self.batch_control_record += validate_field(str(self._entry_hash),
                                                    field_lengths.BATCH_CONTROL_LENGTHS['ENTRY HASH'],
                                                    SHIFT_RIGHT_ADD_ZERO)
        self.batch_control_record += validate_field(
            str(self._total_debit_amount.quantize(decimal.Decimal('.01'))),
            field_lengths.BATCH_CONTROL_LENGTHS['TOTAL DEBIT AMOUNT'],
            SHIFT_RIGHT_ADD_ZERO, True)
        self.batch_control_record += validate_field(
            str(self._total_credit_amount.quantize(decimal.Decimal('.01'))),
            field_lengths.BATCH_CONTROL_LENGTHS['TOTAL CREDIT AMOUNT'],
            SHIFT_RIGHT_ADD_ZERO, True)
        self.batch_control_record += validate_field(self._company_identification_number,
                                                    field_lengths.BATCH_CONTROL_LENGTHS['COMPANY IDENTIFICATION'],
                                                    SHIFT_RIGHT_ADD_ZERO)
        self.batch_control_record += validate_field(self.__authentication_code,
                                                    field_lengths.BATCH_CONTROL_LENGTHS['AUTHENTICATION CODE'],
                                                    SHIFT_LEFT)
        self.batch_control_record += validate_field(self.__reserved, field_lengths.BATCH_CONTROL_LENGTHS['RESERVED'],
                                                    SHIFT_LEFT)
        self.batch_control_record += validate_field(self._originator_dfi_identification,
                                                    field_lengths.BATCH_CONTROL_LENGTHS[
                                                        'ORIGINATING DFI IDENTIFICATION'], SHIFT_LEFT)
        self.batch_control_record += validate_field(self._batch_number,
                                                    field_lengths.BATCH_CONTROL_LENGTHS['BATCH NUMBER'],
                                                    SHIFT_RIGHT_ADD_ZERO)
        self.batch_control_record += '\n'
        return self.batch_control_record


class Entry:
    # The following values are printed:
    _record_type = '6'  # Entry Detail record type is 6.

    def __init__(self, transaction_code, routing_number, account_number,
                 amount, identification_number, receiver_name,
                 discretionary_data, originating_dfi_identification, entry_number):
        self.transaction_code = str(transaction_code)
        self.routing_number = str(routing_number)
        self._account_number = str(account_number)
        self.amount = decimal.Decimal(amount)
        self._identification_number = str(identification_number)
        self._receiver_name = str(receiver_name)
        self._discretionary_data = str(discretionary_data)
        self._originating_dfi_identification = originating_dfi_identification
        self.entry_record = ''
        self.addenda_records = []
        self._local_entry_number = entry_number

    @property
    def has_addenda(self):
        return '1' if self.addenda_records else '0'

    @property
    def addenda_count(self):
        return len(self.addenda_records)

    @property
    def trace_number(self):
        entry_padding = field_lengths.ENTRY_LENGTHS['TRACE NUMBER'] - len(self._originating_dfi_identification)
        return '{0}{1}'.format(self._originating_dfi_identification,
                               str(self._local_entry_number).rjust(entry_padding, '0'))

    def generate(self):
        self.entry_record += validate_field(self._record_type, field_lengths.ENTRY_LENGTHS['RECORD TYPE CODE'])
        self.entry_record += validate_field(self.transaction_code, field_lengths.ENTRY_LENGTHS['TRANSACTION CODE'],
                                            SHIFT_LEFT)
        self.entry_record += validate_field(str(self.routing_number), field_lengths.ENTRY_LENGTHS['RECEIVING DFI ID'],
                                            SHIFT_LEFT)
        self.entry_record += validate_field(self._account_number, field_lengths.ENTRY_LENGTHS['DFI ACCOUNT NUMBER'],
                                            SHIFT_LEFT)
        self.entry_record += validate_field(str(self.amount.quantize(decimal.Decimal('.01'))),
                                            field_lengths.ENTRY_LENGTHS['DOLLAR AMOUNT'], SHIFT_RIGHT_ADD_ZERO, True)
        self.entry_record += validate_field(self._identification_number,
                                            field_lengths.ENTRY_LENGTHS['INDIVIDUAL IDENTIFICATION'],
                                            SHIFT_LEFT)
        self.entry_record += validate_field(self._receiver_name, field_lengths.ENTRY_LENGTHS['INDIVIDUAL NAME'],
                                            SHIFT_LEFT, False)
        self.entry_record += validate_field(self._discretionary_data, field_lengths.ENTRY_LENGTHS['DISCRETIONARY DATA'],
                                            SHIFT_LEFT)
        self.entry_record += validate_field(self.has_addenda, field_lengths.ENTRY_LENGTHS['ADDENDA'], SHIFT_LEFT)
        self.entry_record += validate_field(self.trace_number, field_lengths.ENTRY_LENGTHS['TRACE NUMBER'], SHIFT_LEFT)
        self.entry_record += '\n'
        return self.entry_record[:95]

    def add_addenda(self, main_detail, type_code):
        _entry_record_id = str(self._local_entry_number).rjust(7, '0')
        _addenda_record = Addenda(main_detail, type_code, _entry_record_id, self.addenda_count + 1)
        self.addenda_records.append(_addenda_record)


class Addenda:
    _record_type = '7'  # Addenda records are type 7

    def __init__(self, main_detail, type_code, entry_record_id, addenda_sequence):
        self._main_detail = str(main_detail)
        self._type_code = str(type_code)
        self._entry_record_id = str(entry_record_id)
        self._addenda_sequence = addenda_sequence
        self.addenda_record = ''

    def generate(self):
        self.addenda_record += validate_field(self._record_type, field_lengths.ADDENDA_LENGTHS['RECORD TYPE'])
        self.addenda_record += validate_field(self._type_code, field_lengths.ADDENDA_LENGTHS['TYPE CODE'], SHIFT_LEFT)
        self.addenda_record += validate_field(self._main_detail, field_lengths.ADDENDA_LENGTHS['MAIN DETAIL'],
                                              SHIFT_LEFT, to_alphanumeric=False)
        self.addenda_record += validate_field(str(self._addenda_sequence), field_lengths.ADDENDA_LENGTHS['SEQUENCE'],
                                              SHIFT_RIGHT_ADD_ZERO)
        self.addenda_record += validate_field(self._entry_record_id, field_lengths.ADDENDA_LENGTHS['ENTRY RECORD ID'],
                                              SHIFT_LEFT)
        self.addenda_record += '\n'
        return self.addenda_record


class ACHFile(object):
    def __init__(self):
        self._file_header = None
        self._file_control_record = ''
        self.batch_records = []
        self.destination_name = ''
        self.origin_name = ''
        self.reference_code = ''
        self.entry_class_code = ''
        self.entry_description = ''
        self.descriptive_date = today_with_format
        self.destination_routing_number = ''
        self.company_identification_number = ''
        self.origin_id = ''
        self.id_store = IDStore()
        self.company_account_number = ''
        self.file_name = ''

    @property
    def has_payments(self):
        return any(batch.entry_records for batch in self.batch_records)

    @property
    def entry_count(self):
        return sum(batch.entry_count for batch in self.batch_records)

    @property
    def total_debit_amount(self):
        return sum(batch.total_debit_amount for batch in self.batch_records)

    @property
    def total_credit_amount(self):
        return sum(batch.total_credit_amount for batch in self.batch_records)

    @property
    def entry_hash(self):
        return str(sum(batch.entry_hash for batch in self.batch_records))[-10:]

    @property
    def batch_count(self):
        return len(self.batch_records)

    def get_next_batch_number(self):
        return len(self.batch_records) + 1

    def create_header(self):
        self._file_header = FileHeader(self.destination_routing_number,
                                       self.origin_id,
                                       self.destination_name,
                                       self.origin_name,
                                       self.reference_code)

    def new_batch(self, dfi_number, batch_name, entry_description=None,
                  company_identification_number=None,
                  entry_class_code=None, discretionary_data='',
                  service_class=MIXED, effective_entry_delay=1):
        if entry_description is None:
            entry_description = self.entry_description
        if company_identification_number is None:
            company_identification_number = self.company_identification_number
        if entry_class_code is None:
            entry_class_code = self.entry_class_code
        new_batch = BatchHeader(batch_name, discretionary_data,
                                company_identification_number,
                                entry_class_code, entry_description,
                                dfi_number, self.get_next_batch_number(), self.id_store,
                                description_date=self.descriptive_date, service_class=service_class,
                                effective_entry_delay=effective_entry_delay)
        self.batch_records.append(new_batch)

    def save(self, file_path):
        for batch in self.batch_records:
            batch.finalize()
        line_count = (self.batch_count * 2) + self.entry_count + 2
        block_count, footer_lines = divmod(line_count, 10)
        footer_lines = 10 - footer_lines
        if footer_lines:
            block_count += 1
        self._file_control_record = FileControl(self.batch_count, block_count,
                                                self.entry_count, self.entry_hash,
                                                self.total_debit_amount, self.total_credit_amount)
        try:
            os.makedirs(os.path.split(file_path)[0])
        except FileExistsError:
            pass  # If the folder exists, don't try to create it.

        with open(file_path, 'w+') as ach_file:
            file_header = self._file_header.generate()
            ach_file.write(file_header)
            for batch in self.batch_records:
                ach_file.write(batch.generate())
                for entry in batch.entry_records:
                    entry_record = entry.generate()
                    ach_file.write(entry_record)
                    for addenda in entry.addenda_records:
                        addenda_record = addenda.generate()
                        ach_file.write(addenda_record)
                ach_file.write(batch.batch_control_record)
            file_control_record = self._file_control_record.generate()
            ach_file.write(file_control_record)

            if footer_lines > 0:
                line = '\n'.ljust(95, '9')
                for x in range(0, footer_lines):
                    ach_file.write(line)
        self.file_name = file_path
