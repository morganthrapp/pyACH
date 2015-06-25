__author__ = 'Morgan Thrapp'

import unittest
import os
from random import randint

from loremipsum import get_sentence

from pyach import ACHRecordTypes


output_file_path = os.getcwd() + os.path.sep + 'test_file.txt'


class TestACHRecord(unittest.TestCase):
    ach_file = ACHRecordTypes.ACHFile()
    ach_file.batch_name = get_sentence()
    ach_file.destination_name = get_sentence()
    ach_file.destination_routing_number = randint(111111111, 999999999)
    ach_file.entry_class_code = get_sentence()
    ach_file.entry_description = get_sentence()
    ach_file.header_discretionary_data = get_sentence()
    ach_file.originRoutingNumber = get_sentence()
    ach_file.origin_name = get_sentence()
    ach_file.reference_code = get_sentence()
    ach_file.originRoutingNumber = randint(111111111, 999999999)

    def test_file_header(self):
        self.ach_file.create_header()
        file_header = self.ach_file._file_header.generate()
        self.assertEqual(len(file_header), 95)
        self.assertEqual(file_header[:1], '1')
        self.assertEqual(file_header[1:3], '01')
        self.assertEqual(file_header[34:37], '094')
        self.assertEqual(file_header[37:39], '10')
        self.assertEqual(file_header[39:40], '1')

    def test_batch_header(self):
        self.ach_file.new_batch(randint(111111111, 999999999), get_sentence())
        test_batch = self.ach_file.batch_records[-1].generate()
        self.assertEqual(len(test_batch), 95)
        self.assertEqual(test_batch[:1], '5')
        self.assertEqual(test_batch[75:78], '   ')
        self.assertEqual(test_batch[78:79], '1')

    def test_entry_record_without_addenda(self):
        self.ach_file.batch_records[-1].add_entry(ACHRecordTypes.CHECK_DEPOSIT,
                                                  randint(111111111, 999999999), randint(111111111, 999999999),
                                                  randint(111111111, 999999999), randint(111111111, 999999999),
                                                  get_sentence())
        test_entry_record = self.ach_file.batch_records[-1].entry_records[-1]
        test_entry = test_entry_record.generate()
        self.assertEqual(len(test_entry), 95)
        self.assertEqual(test_entry[:1], '6')

    def test_entry_record_with_addenda(self):
        self.ach_file.batch_records[-1].add_entry(ACHRecordTypes.CHECK_DEPOSIT,
                                                  randint(111111111, 999999999), randint(111111111, 999999999),
                                                  randint(111111111, 999999999), get_sentence(), get_sentence())
        entry_record = self.ach_file.batch_records[-1].entry_records[-1]
        entry_record.add_addenda('test', ACHRecordTypes.CCD)
        addenda_record = entry_record.addenda_records[-1]
        test_addenda = addenda_record.generate()
        self.assertEqual(len(test_addenda), 95)
        self.assertEqual(test_addenda[:1], '7')


class TestAchSave(unittest.TestCase):
    save_ach_file = ACHRecordTypes.ACHFile()
    save_ach_file.batch_name = get_sentence()
    save_ach_file.destination_name = get_sentence()
    save_ach_file.destination_routing_number = randint(111111111, 999999999)
    save_ach_file.entry_class_code = get_sentence()
    save_ach_file.entry_description = get_sentence()
    save_ach_file.header_discretionary_data = get_sentence()
    save_ach_file.origin_name = get_sentence()
    save_ach_file.reference_code = get_sentence()
    save_ach_file.originRoutingNumber = randint(111111111, 999999999)
    test_batch_control = ''
    test_file_control = ''
    file_control = ''
    line_count = 0
    entry_addenda_count = 0
    save_ach_file.create_header()
    save_ach_file.new_batch(get_sentence(), get_sentence())
    for x in range(0, 10):
        save_ach_file.batch_records[-1].add_entry(ACHRecordTypes.CHECK_DEPOSIT,
                                                  randint(111111111, 999999999), randint(111111111, 999999999),
                                                  randint(111111111, 999999999), randint(111111111, 999999999),
                                                  get_sentence())
        save_ach_file.batch_records[-1].entry_records[-1].add_addenda(get_sentence(), ACHRecordTypes.CCD)
    save_ach_file.save(output_file_path)

    for line in open(output_file_path):
        record_type = line[:1]
        if record_type == '1':
            file_header = line
        elif record_type == '5':
            batch_header = line
        elif record_type == '6':
            entry_record = line
            entry_addenda_count += 1
        elif record_type == '7':
            addenda_record = line
            entry_addenda_count += 1
        elif record_type == '8':
            batch_control = line
        elif record_type == '9' and file_control == '':
            file_control = line
        line_count += 1

    def test_file_header_line(self):
        self.assertEqual(self.file_header[:1], '1')
        self.assertEqual(self.file_header[1:3], '01')
        self.assertEqual(self.file_header[34:37], '094')
        self.assertEqual(self.file_header[37:39], '10')
        self.assertEqual(self.file_header[39:40], '1')
        file_header_length = len(self.file_header)
        self.assertEqual(file_header_length, 95)

    def test_batch_header_line(self):
        self.assertEqual(self.batch_header[:1], '5')
        self.assertFalse(self.batch_header[76:78].strip())
        self.assertEqual(self.batch_header[78:79], '1')
        batch_header_length = len(self.batch_header)
        self.assertEqual(batch_header_length, 95)

    def test_entry_line(self):
        self.assertEqual(self.entry_record[:1], '6')
        entry_length = len(self.entry_record)
        self.assertEqual(entry_length, 95)

    def test_addenda_line(self):
        self.assertEqual(self.addenda_record[:1], '7')
        addenda_length = len(self.addenda_record)
        self.assertEqual(addenda_length, 95)

    def test_batch_control_record(self):
        self.assertEqual(self.batch_control[:1], '8')
        self.assertFalse(self.batch_control[74:79].strip())
        self.assertEqual(self.entry_addenda_count, int(self.batch_control[5:10]))
        batch_control_length = len(self.batch_control)
        self.assertEqual(batch_control_length, 95)

    def test_file_control_record(self):
        self.assertEqual(self.file_control[:1], '9')
        self.assertEqual((self.line_count % 10), 0)
        block_count, _ = divmod(self.line_count, 10)
        self.assertEqual(block_count, int(self.file_control[8:13]))
        file_control_length = len(self.file_control)
        self.assertEqual(file_control_length, 95)

if __name__ == '__main__':
    test_classes_to_run = [TestACHRecord, TestAchSave]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
