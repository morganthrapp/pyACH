__author__ = 'Morgan Thrapp'

import unittest
import os

import ACHRecordTypes


output_file_path = os.getcwd() + '\\test_file.txt'


class TestACHRecord(unittest.TestCase):
    test_ACH_file = ACHRecordTypes.ACHFile()
    test_ACH_file.batch_name = 'TEST'
    test_ACH_file.destination_routing_number = 'TEST'
    test_ACH_file.destination_name = 'TEST'
    test_ACH_file.destination_routing_number = '9999'
    test_ACH_file.entry_class_code = 'WEB'
    test_ACH_file.entry_description = 'TEST'
    test_ACH_file.header_discretionary_data = 'TEST'
    test_ACH_file.originRoutingNumber = 'TEST'
    test_ACH_file.origin_name = 'TEST'
    test_ACH_file.reference_code = 'TEST'
    test_ACH_file.originRoutingNumber = '9999'

    def test_file_header(self):
        self.test_ACH_file.create_header()
        file_header = self.test_ACH_file._file_header.generate()
        self.assertEqual(len(file_header), 95)
        self.assertEqual(file_header[:1], '1')
        self.assertEqual(file_header[1:3], '01')
        self.assertEqual(file_header[34:37], '094')
        self.assertEqual(file_header[37:39], '10')
        self.assertEqual(file_header[39:40], '1')

    def test_batch_header(self):
        self.test_ACH_file.new_batch('999')
        test_batch = self.test_ACH_file.batch_records[-1].generate()
        self.assertEqual(len(test_batch), 95)
        self.assertEqual(test_batch[:1], '5')
        self.assertEqual(test_batch[75:78], '   ')
        self.assertEqual(test_batch[78:79], '1')

    def test_entry_record_without_addenda(self):
        self.test_ACH_file.batch_records[-1].add_entry(ACHRecordTypes.CHECK_DEPOSIT, '07640125', '9999',
                                                       '1234.56', '9999', 'test')
        test_entry = self.test_ACH_file.batch_records[-1].entry_records[-1].generate()
        self.assertEqual(len(test_entry), 95)
        self.assertEqual(test_entry[:1], '6')
        self.assertEqual(test_entry[36:37], '.')

    def test_entry_record_with_addenda(self):
        self.test_ACH_file.batch_records[-1].add_entry(ACHRecordTypes.CHECK_DEPOSIT, '07640125', '9999',
                                                       '1234.56', '9999', 'test')
        self.test_ACH_file.batch_records[-1].entry_records[-1].add_addenda('test', ACHRecordTypes.CCD)
        test_addenda = self.test_ACH_file.batch_records[-1].entry_records[-1].addenda_records[-1].generate()
        self.assertEqual(len(test_addenda), 95)
        self.assertEqual(test_addenda[:1], '7')


class TestAchSave(unittest.TestCase):
    test_save_ACH_file = ACHRecordTypes.ACHFile()
    test_save_ACH_file.batch_name = 'TEST'
    test_save_ACH_file.destination_routing_number = 'TEST'
    test_save_ACH_file.destination_name = 'TEST'
    test_save_ACH_file.destination_routing_number = '9999'
    test_save_ACH_file.entry_class_code = 'WEB'
    test_save_ACH_file.entry_description = 'TEST'
    test_save_ACH_file.header_discretionary_data = 'TEST'
    test_save_ACH_file.origin_name = 'TEST'
    test_save_ACH_file.reference_code = 'TEST'
    test_save_ACH_file.originRoutingNumber = '9999'
    test_batch_control = ''
    test_file_control = ''

    def test_save(self):
        self.test_save_ACH_file.create_header()
        self.test_save_ACH_file.new_batch('999')
        self.test_save_ACH_file.batch_records[0].add_entry(ACHRecordTypes.CHECK_DEPOSIT, '07640125', '9999', '1234.56',
                                                           '9999', 'test')
        self.test_save_ACH_file.batch_records[0].entry_records[0].add_addenda('test', ACHRecordTypes.CCD)
        self.test_save_ACH_file.save(output_file_path)

    for line in open(output_file_path):
        record_type = line[:1]
        if record_type == '1':
            file_header = line
        elif record_type == '5':
            batch_header = line
        elif record_type == '6':
            entry_record = line
        elif record_type == '7':
            addenda_record = line
        elif record_type == '8':
            batch_control = line
        elif record_type == '9':
            file_control = line

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
        batch_control_length = len(self.batch_control)
        self.assertEqual(batch_control_length, 95)

    def test_file_control_record(self):
        self.assertEqual(self.file_control[:1], '9')
        self.assertFalse(self.file_control[56:94].strip())
        file_control_length = len(self.file_control)
        self.assertEqual(file_control_length, 94)


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
