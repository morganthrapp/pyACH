import datetime
import os
import itertools

import pytest

import pyach.ACHRecordTypes

output_file_path = os.path.join(os.path.dirname(__file__), 'ach_file.txt')


def eq(x, y=None):  # pragma: no cover
    if y is not None:
        assert x == y
    else:
        assert x


DESTINATION_ROUTING_NUMBER = '123456789'
ORIGIN_ROUTING_NUMBER = '987654321'
DFI_NUMBER = '19283746'
BATCH_NAME = 'TESTBATCH'
ACCOUNT_NUMBER = '918273645'
AMOUNTS = [1423.89, 32314.01, '9023.09', 444.03, 951729.01]
FILE_AMOUNTS = list(map(lambda x: str(x).replace('.', ''), AMOUNTS))
MANUAL_SUM = 99493403
AMOUNT = '1234567.89'
FILE_AMOUNT = '0123456789'
COMPANY_IDENTIFICATION_NUMBER = '1232789456'
TODAY = '160517'
EFFECTIVE_ENTRY_DATE = '160621'
NOW = '1108'
DESTINATION_NAME = 'TheIronBankOfBravos'
ORIGIN_NAME = 'AryaStark'
REFERENCE_CODE = 'ETOOREAL'
DISCRETIONARY_DATA = 'Valar Morghulis'
ENTRY_CLASS_CODE = 'PPD'
ENTRY_DESCRIPTION = 'TestPay'
INDIVIDUAL_IDENTIFICATION_NUMBER = '675849302123'
RECEIVER_NAME = "jaqen h'ghar"
ENTRY_HASH = '0123456780'


class TestACHRecord:
    @pytest.fixture
    def ach_file(self, monkeypatch):
        monkeypatch.setattr(pyach.ACHRecordTypes, 'today_with_format', TODAY)
        monkeypatch.setattr(pyach.ACHRecordTypes, 'now_with_format', NOW)
        monkeypatch.setattr(datetime, 'datetime', FakeDate)
        ach_file = pyach.ACHRecordTypes.ACHFile()
        ach_file.batch_name = BATCH_NAME
        ach_file.destination_name = DESTINATION_NAME
        ach_file.destination_routing_number = DESTINATION_ROUTING_NUMBER
        ach_file.entry_class_code = ENTRY_CLASS_CODE
        ach_file.entry_description = ENTRY_DESCRIPTION
        ach_file.origin_name = ORIGIN_NAME
        ach_file.reference_code = REFERENCE_CODE
        ach_file.origin_routing_number = ORIGIN_ROUTING_NUMBER
        ach_file.origin_id = COMPANY_IDENTIFICATION_NUMBER
        ach_file.company_identification_number = COMPANY_IDENTIFICATION_NUMBER
        ach_file.create_header()
        ach_file.new_batch(DFI_NUMBER, BATCH_NAME, discretionary_data=DISCRETIONARY_DATA)
        return ach_file

    def test_file_header(self, ach_file):
        file_header = ach_file._file_header.generate()
        eq(len(file_header), 95)
        eq(file_header[:1], '1')
        eq(file_header[1:3], '01')
        eq(file_header[3:13].strip(), DESTINATION_ROUTING_NUMBER)
        eq(file_header[13:23], COMPANY_IDENTIFICATION_NUMBER)
        eq(file_header[23:29], TODAY)
        eq(file_header[29:33], NOW)
        eq(file_header[33], 'A')
        eq(file_header[34:37], '094')
        eq(file_header[37:39], '10')
        eq(file_header[39:40], '1')
        eq(file_header[40:63].strip(), DESTINATION_NAME)
        eq(file_header[63:86].strip(), ORIGIN_NAME)
        eq(file_header[86:94].strip(), REFERENCE_CODE)

    def test_batch_header(self, ach_file):
        test_batch = ach_file.batch_records[-1].generate()
        eq(len(test_batch), 95)
        eq(test_batch[:1], '5')
        eq(test_batch[1:4].strip(), '200')
        eq(test_batch[4:20].strip(), BATCH_NAME)
        eq(test_batch[20:40].strip(), DISCRETIONARY_DATA)
        eq(test_batch[40:50].strip(), COMPANY_IDENTIFICATION_NUMBER)
        eq(test_batch[50:53], ENTRY_CLASS_CODE)
        eq(test_batch[53:63].strip(), ENTRY_DESCRIPTION)
        eq(test_batch[63:69], TODAY)
        eq(test_batch[69:75], EFFECTIVE_ENTRY_DATE)
        eq(test_batch[75:78], '   ')
        eq(test_batch[78], '1')
        eq(test_batch[79:87], DFI_NUMBER)
        eq(int(test_batch[87:94]), 1)

    def test_entry_record_without_addenda(self, ach_file):
        ach_file.batch_records[-1].add_entry(pyach.ACHRecordTypes.CHECK_DEPOSIT, DESTINATION_ROUTING_NUMBER,
                                             ACCOUNT_NUMBER, AMOUNT, COMPANY_IDENTIFICATION_NUMBER,
                                             RECEIVER_NAME)
        test_entry_record = ach_file.batch_records[-1].entry_records[-1]
        test_entry = test_entry_record.generate()
        eq(len(test_entry), 95)
        eq(test_entry[0], '6')
        eq(test_entry[1:3], pyach.ACHRecordTypes.CHECK_DEPOSIT)
        eq(test_entry[3:12], DESTINATION_ROUTING_NUMBER)
        eq(test_entry[12:29].strip(), ACCOUNT_NUMBER)
        eq(test_entry[29:39], FILE_AMOUNT)
        eq(test_entry[39:54].strip(), COMPANY_IDENTIFICATION_NUMBER)
        eq(test_entry[54:76].strip(), RECEIVER_NAME)
        eq(test_entry[76:78], '  ')
        eq(test_entry[78], '0')
        eq(test_entry[79:94], DFI_NUMBER + '0000001')

    def test_entry_record_with_addenda(self, ach_file):
        ach_file.batch_records[-1].add_entry(pyach.ACHRecordTypes.CHECK_DEPOSIT, DESTINATION_ROUTING_NUMBER,
                                             ACCOUNT_NUMBER, AMOUNT, COMPANY_IDENTIFICATION_NUMBER,
                                             RECEIVER_NAME, DISCRETIONARY_DATA)
        entry_record = ach_file.batch_records[-1].entry_records[-1]
        entry_record.add_addenda('test', pyach.ACHRecordTypes.CCD)
        test_entry = entry_record.generate()
        addenda_record = entry_record.addenda_records[-1]
        test_addenda = addenda_record.generate()
        eq(len(test_addenda), 95)
        eq(test_addenda[0], '7')
        eq(test_addenda[1:3], pyach.ACHRecordTypes.CCD)
        eq(test_addenda[3:83].strip(), 'test')
        eq(test_addenda[83:87], '0001')
        eq(test_addenda[87:94], '0000001')
        eq(test_entry[78], '1')


class TestAchSave:
    @pytest.fixture
    def save_ach_file(self, monkeypatch):
        monkeypatch.setattr(pyach.ACHRecordTypes, 'today_with_format', TODAY)
        monkeypatch.setattr(pyach.ACHRecordTypes, 'now_with_format', NOW)
        monkeypatch.setattr(datetime, 'datetime', FakeDate)
        save_ach_file = pyach.ACHRecordTypes.ACHFile()
        save_ach_file.batch_name = BATCH_NAME
        save_ach_file.destination_name = DESTINATION_NAME
        save_ach_file.destination_routing_number = DESTINATION_ROUTING_NUMBER
        save_ach_file.entry_class_code = ENTRY_CLASS_CODE
        save_ach_file.entry_description = ENTRY_DESCRIPTION
        save_ach_file.header_discretionary_data = DISCRETIONARY_DATA
        save_ach_file.origin_name = ORIGIN_NAME
        save_ach_file.reference_code = REFERENCE_CODE
        save_ach_file.origin_routing_number = ORIGIN_ROUTING_NUMBER
        save_ach_file.origin_id = COMPANY_IDENTIFICATION_NUMBER
        save_ach_file.company_identification_number = COMPANY_IDENTIFICATION_NUMBER
        save_ach_file.create_header()
        save_ach_file.new_batch(DFI_NUMBER, BATCH_NAME, discretionary_data=DISCRETIONARY_DATA)
        for amount in AMOUNTS:
            save_ach_file.batch_records[-1].add_entry(pyach.ACHRecordTypes.CHECK_DEPOSIT, DESTINATION_ROUTING_NUMBER,
                                                      ACCOUNT_NUMBER, amount, INDIVIDUAL_IDENTIFICATION_NUMBER,
                                                      RECEIVER_NAME)
            save_ach_file.batch_records[-1].entry_records[-1].add_addenda('test',
                                                                          pyach.ACHRecordTypes.CCD)
            save_ach_file.batch_records[-1].add_entry(pyach.ACHRecordTypes.CHECK_DEBIT, DESTINATION_ROUTING_NUMBER,
                                                      ACCOUNT_NUMBER, amount, INDIVIDUAL_IDENTIFICATION_NUMBER,
                                                      RECEIVER_NAME)
        save_ach_file.save(output_file_path)
        return save_ach_file

    @pytest.fixture
    def lines(self, save_ach_file):
        line_dict = {}
        with open(save_ach_file.file_name) as file:
            for line in file:
                line_dict.setdefault(line[:1], []).append(line)
        return line_dict

    @pytest.fixture
    def file_header(self, lines):
        return lines['1'][0]

    @pytest.fixture
    def batch_header(self, lines):
        return lines['5'][0]

    @pytest.fixture
    def entry_records(self, lines):
        return lines['6']

    @pytest.fixture
    def detail_count(self, lines):
        return len(lines['6']) + len(lines['7'])

    @pytest.fixture
    def addenda_records(self, lines):
        return lines['7']

    @pytest.fixture
    def batch_control(self, lines):
        return lines['8'][0]

    @pytest.fixture
    def file_control(self, lines):
        return lines['9'][0]

    @pytest.fixture
    def line_count(self, lines):
        return sum(len(val) for val in lines.values())

    def test_file_header_line(self, file_header):
        eq(file_header[0], '1')
        eq(file_header[1:3], '01')
        eq(file_header[3:13].strip(), DESTINATION_ROUTING_NUMBER)
        eq(file_header[13:23].strip(), COMPANY_IDENTIFICATION_NUMBER)
        eq(file_header[23:29], TODAY)
        eq(file_header[29:33], NOW)
        eq(file_header[33], 'A')
        eq(file_header[34:37], '094')
        eq(file_header[37:39], '10')
        eq(file_header[39], '1')
        eq(file_header[40:63].strip(), DESTINATION_NAME)
        eq(file_header[63:86].strip(), ORIGIN_NAME)
        eq(file_header[86:94], REFERENCE_CODE)
        file_header_length = len(file_header)
        eq(file_header_length, 95)

    def test_batch_header_line(self, batch_header):
        eq(batch_header[0], '5')
        eq(batch_header[1:4], pyach.ACHRecordTypes.MIXED)
        eq(batch_header[4:20].strip(), BATCH_NAME)
        eq(batch_header[20:40].strip(), DISCRETIONARY_DATA)
        eq(batch_header[40:50], COMPANY_IDENTIFICATION_NUMBER)
        eq(batch_header[50:53].strip(), ENTRY_CLASS_CODE)
        eq(batch_header[53:63].strip(), ENTRY_DESCRIPTION)
        eq(batch_header[63:69], TODAY)
        eq(batch_header[69:75], EFFECTIVE_ENTRY_DATE)
        eq(batch_header[75:78], '   ')
        eq(batch_header[78], '1')
        eq(batch_header[79:87], DFI_NUMBER)
        eq(int(batch_header[87:94]), 1)
        batch_header_length = len(batch_header)
        eq(batch_header_length, 95)

    def test_entry_line(self, entry_records):
        def get_test_values():
            payment_type_cycle = itertools.cycle([pyach.ACHRecordTypes.CHECK_DEPOSIT, pyach.ACHRecordTypes.CHECK_DEBIT])
            return zip(itertools.chain.from_iterable(zip(FILE_AMOUNTS, FILE_AMOUNTS)), entry_records,
                       payment_type_cycle)

        for index, (amount, entry_record, entry_class_code) in enumerate(get_test_values(), 1):
            eq(entry_record[0], '6')
            eq(entry_record[1:3], entry_class_code)
            eq(entry_record[3:12], DESTINATION_ROUTING_NUMBER)
            eq(entry_record[12:29].strip(), ACCOUNT_NUMBER)
            eq(entry_record[29:39].lstrip('0'), amount)
            eq(entry_record[39:54].strip(), INDIVIDUAL_IDENTIFICATION_NUMBER)
            eq(entry_record[54:76].strip(), RECEIVER_NAME)
            eq(entry_record[76:78], '  ')
            eq(int(entry_record[78]), entry_class_code == pyach.ACHRecordTypes.CHECK_DEPOSIT)
            eq(entry_record[79:94], DFI_NUMBER + str(index).rjust(7, '0'))
            entry_length = len(entry_record)
            eq(entry_length, 95)

    def test_addenda_line(self, addenda_records):
        for index, addenda_record in enumerate(addenda_records, 1):
            eq(addenda_record[0], '7')
            eq(addenda_record[1:3], pyach.ACHRecordTypes.CCD)
            eq(addenda_record[3:83].strip(), 'test')
            eq(int(addenda_record[83:87]), 1)
            eq(int(addenda_record[87:94]), 1 + ((index - 1) * 2))
            addenda_length = len(addenda_record)
            eq(addenda_length, 95)

    def test_batch_control_record(self, batch_control, detail_count):
        eq(batch_control[0], '8')
        eq(batch_control[1:4], pyach.ACHRecordTypes.MIXED)
        eq(int(batch_control[4:10]), detail_count)
        eq(batch_control[10:20], ENTRY_HASH)
        eq(int(batch_control[20:32]), MANUAL_SUM)
        eq(int(batch_control[32:44]), MANUAL_SUM)
        eq(batch_control[44:54], COMPANY_IDENTIFICATION_NUMBER)
        eq(batch_control[54:73].strip(), '')
        eq(batch_control[73:79], '      ')
        eq(batch_control[79:87], DFI_NUMBER)
        eq(int(batch_control[87:94]), 1)
        batch_control_length = len(batch_control)
        eq(batch_control_length, 95)

    def test_file_control_record(self, file_control, line_count, detail_count):
        eq(file_control[0], '9')
        eq(int(file_control[1:7]), 1)
        eq(int(file_control[7:13]), 2)
        eq(int(file_control[13:21]), detail_count)
        eq(file_control[21:31], ENTRY_HASH)
        eq(int(file_control[31:43]), MANUAL_SUM)
        eq(int(file_control[43:55]), MANUAL_SUM)
        eq(file_control[55:94].strip(), '')
        eq(line_count, 20)
        eq((line_count % 10), 0)
        block_count, _ = divmod(line_count, 10)
        eq(block_count, int(file_control[8:13]))
        file_control_length = len(file_control)
        eq(file_control_length, 95)

    def test_has_payments(self, save_ach_file):
        assert save_ach_file.has_payments


class FakeDate:
    FAKE_DAY = datetime.datetime(year=2016, month=6, day=20)

    @classmethod
    def today(cls):
        return cls.FAKE_DAY


class FakeWeekendDate:
    FAKE_DAY = datetime.datetime(year=2016, month=10, day=29)

    @classmethod
    def today(cls):
        return cls.FAKE_DAY


def test_effective_entry_date(monkeypatch):
    monkeypatch.setattr(datetime, 'datetime', FakeDate)
    eq(pyach.ACHRecordTypes.get_effective_entry_date(0), '160620')
    eq(pyach.ACHRecordTypes.get_effective_entry_date(1), '160621')
    eq(pyach.ACHRecordTypes.get_effective_entry_date(1, as_date=True), FakeDate.FAKE_DAY + datetime.timedelta(days=1))
    eq(pyach.ACHRecordTypes.get_effective_entry_date(1), '160621')
    eq(pyach.ACHRecordTypes.get_effective_entry_date(5), '160627')
    eq(pyach.ACHRecordTypes.get_effective_entry_date(9), '160701')


def test_effective_entry_date_on_weekend(monkeypatch):
    monkeypatch.setattr(datetime, 'datetime', FakeWeekendDate)
    eq(pyach.ACHRecordTypes.get_effective_entry_date(1), '161101')
    eq(pyach.ACHRecordTypes.get_effective_entry_date(1), '161101')
