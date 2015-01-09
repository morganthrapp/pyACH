__author__ = 'Morgan Thrapp'

import unittest

import ACHRecordTypes


testFilePath = 'C:/ACH/testFile.txt'


class TestACHRecord(unittest.TestCase):
    testACHFile = ACHRecordTypes.ACHFile()
    testACHFile.batchName = 'TEST'
    testACHFile.destinationRoutingNumber = 'TEST'
    testACHFile.destinationName = 'TEST'
    testACHFile.destinationRoutingNumber = '9999'
    testACHFile.entryClassCode = 'WEB'
    testACHFile.entryDescription = 'TEST'
    testACHFile.headerDiscretionaryData = 'TEST'
    testACHFile.originRoutingNumber = 'TEST'
    testACHFile.originName = 'TEST'
    testACHFile.referenceCode = 'TEST'
    testACHFile.originRoutingNumber = '9999'

    def test_file_header(self):
        self.testACHFile.create_header()
        file_header = self.testACHFile._fileHeader.generate()
        self.assertEqual(len(file_header), 95)
        self.assertEqual(file_header[:1], '1')
        self.assertEqual(file_header[1:3], '01')
        self.assertEqual(file_header[34:37], '094')
        self.assertEqual(file_header[37:39], '10')
        self.assertEqual(file_header[39:40], '1')

    def test_batch_header(self):
        self.testACHFile.new_batch('999')
        test_batch = self.testACHFile.batchRecords[0].generate()
        self.assertEqual(len(test_batch), 95)
        self.assertEqual(test_batch[:1], '5')
        self.assertEqual(test_batch[75:78], '   ')
        self.assertEqual(test_batch[78:79], '1')

    def test_entry_record_without_addenda(self):
        self.testACHFile.batchRecords[0].add_entry(ACHRecordTypes.CHECK_DEPOSIT, '07640125', '9999', '1234.56', '9999',
                                                   'test')
        test_entry = self.testACHFile.batchRecords[0].entryRecords[0].generate()
        self.assertEqual(len(test_entry), 95)
        self.assertEqual(test_entry[:1], '6')
        self.assertEqual(test_entry[36:37], '.')

    def test_entry_record_with_addenda(self):
        self.testACHFile.batchRecords[0].add_entry(ACHRecordTypes.CHECK_DEPOSIT, '07640125', '9999', '1234.56', '9999',
                                                   'test')
        self.testACHFile.batchRecords[0].entryRecords[0].add_addenda('test', ACHRecordTypes.CCD)
        test_addenda = self.testACHFile.batchRecords[0].entryRecords[0].addendaRecords[0].generate()
        self.assertEqual(len(test_addenda), 95)
        self.assertEqual(test_addenda[:1], '7')


class TestAchSave(unittest.TestCase):
    testSaveACHFile = ACHRecordTypes.ACHFile()
    testSaveACHFile.batchName = 'TEST'
    testSaveACHFile.destinationRoutingNumber = 'TEST'
    testSaveACHFile.destinationName = 'TEST'
    testSaveACHFile.destinationRoutingNumber = '9999'
    testSaveACHFile.entryClassCode = 'WEB'
    testSaveACHFile.entryDescription = 'TEST'
    testSaveACHFile.headerDiscretionaryData = 'TEST'
    testSaveACHFile.originName = 'TEST'
    testSaveACHFile.referenceCode = 'TEST'
    testSaveACHFile.originRoutingNumber = '9999'
    test_batch_control = ''
    test_file_control = ''

    def test_save(self):
        self.testSaveACHFile.create_header()
        self.testSaveACHFile.new_batch('999')
        self.testSaveACHFile.batchRecords[0].add_entry(ACHRecordTypes.CHECK_DEPOSIT, '07640125', '9999', '1234.56',
                                                       '9999', 'test')
        self.testSaveACHFile.batchRecords[0].entryRecords[0].add_addenda('test', ACHRecordTypes.CCD)
        self.testSaveACHFile.save(testFilePath)


class TestAfterSaveFile(unittest.TestCase):
    for line in open(testFilePath):
        record_type = line[:1]
        if record_type == '1':
            fileHeader = line
        elif record_type == '5':
            batchHeader = line
        elif record_type == '6':
            entryRecord = line
        elif record_type == '7':
            addendaRecord = line
        elif record_type == '8':
            batchControl = line
        elif record_type == '9':
            fileControl = line

    def test_file_header_line(self):
        self.assertEqual(self.fileHeader[:1], '1')
        self.assertEqual(self.fileHeader[1:3], '01')
        self.assertEqual(self.fileHeader[34:37], '094')
        self.assertEqual(self.fileHeader[37:39], '10')
        self.assertEqual(self.fileHeader[39:40], '1')
        file_header_length = len(self.fileHeader)
        self.assertEqual(file_header_length, 95)

    def test_batch_header_line(self):
        self.assertEqual(self.batchHeader[:1], '5')
        self.assertFalse(self.batchHeader[76:78].strip())
        self.assertEqual(self.batchHeader[78:79], '1')
        batch_header_length = len(self.batchHeader)
        self.assertEqual(batch_header_length, 95)

    def test_entry_line(self):
        self.assertEqual(self.entryRecord[:1], '6')
        entry_length = len(self.entryRecord)
        self.assertEqual(entry_length, 95)

    def test_addenda_line(self):
        self.assertEqual(self.addendaRecord[:1], '7')
        addenda_length = len(self.addendaRecord)
        self.assertEqual(addenda_length, 95)

    def test_batch_control_record(self):
        self.assertEqual(self.batchControl[:1], '8')
        self.assertFalse(self.batchControl[74:79].strip())
        batch_control_length = len(self.batchControl)
        self.assertEqual(batch_control_length, 95)

    def test_file_control_record(self):
        self.assertEqual(self.fileControl[:1], '9')
        self.assertFalse(self.fileControl[56:94].strip())
        file_control_length = len(self.fileControl)
        self.assertEqual(file_control_length, 94)


if __name__ == '__main__':
    test_classes_to_run = [TestACHRecord, TestAchSave, TestAfterSaveFile]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
