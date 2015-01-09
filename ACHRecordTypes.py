__author__ = 'Morgan Thrapp'

import datetime

todayWithFormat = datetime.date.today().strftime('%y%m%d')
nowWithFormat = datetime.datetime.now().time().strftime('%H%M')
yesterday = datetime.datetime.now() - datetime.timedelta(1)
yesterdayWithFormat = yesterday.strftime('%y%m%d')


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


class FileHeader:
    _recordType = '1'  # ACH Header records are type 1
    _priorityCode = '01'  # 01 is the only code supported by NACHA
    _recordSize = '094'
    _blockingFactor = '10'
    _formatCode = '1'

    def __init__(self, destination_routing_number, company_identification_number, destination_name, origin_name,
                 reference_code):
        self._destinationRoutingNumber = str(destination_routing_number).ljust(10)
        self._companyIdentificationNumber = str(company_identification_number).ljust(10)
        self._destinationName = str(destination_name).ljust(23)
        self._originName = str(origin_name).ljust(23)
        self._referenceCode = str(reference_code).ljust(8)
        self._creationDate = todayWithFormat
        self._creationTime = nowWithFormat
        self._fileIDModifier = 'A'  # First file of the day should have A. Subsequent files follow pattern A-Z/1-9
        self.fileHeaderRecord = ''

    def generate(self):
        self.fileHeaderRecord += self._recordType
        self.fileHeaderRecord += self._priorityCode
        self.fileHeaderRecord += self._destinationRoutingNumber
        self.fileHeaderRecord += self._companyIdentificationNumber
        self.fileHeaderRecord += self._creationDate
        self.fileHeaderRecord += self._creationTime
        self.fileHeaderRecord += self._fileIDModifier
        self.fileHeaderRecord += self._recordSize
        self.fileHeaderRecord += self._blockingFactor
        self.fileHeaderRecord += self._formatCode
        self.fileHeaderRecord += self._destinationName
        self.fileHeaderRecord += self._originName
        self.fileHeaderRecord += self._referenceCode
        self.fileHeaderRecord += '\n'
        self._fileIDModifier = chr(ord(self._fileIDModifier) + 1)
        return self.fileHeaderRecord


class FileControl:
    _recordType = '9'  # ACH File Control records are type 9
    __reserved = ''.ljust(39)  # DO NOT MODIFY THIS. It needs to be blank.

    def __init__(self, batch_count, block_count, entry_count, entry_hash,
                 total_debt_amount, total_credit_amount):
        self._batchCount = str(batch_count).rjust(6, '0')
        self._blockCount = str(block_count).rjust(6, '0')
        self._entryCount = str(entry_count).rjust(8, '0')
        self._entryHash = str(entry_hash).ljust(10)
        self._totalDebitAmount = str(total_debt_amount).rjust(12, '0')
        self._totalCreditAmount = str(total_credit_amount).rjust(12, '0')
        self.fileControlRecord = ''

    def generate(self):
        self.fileControlRecord += self._recordType
        self.fileControlRecord += self._batchCount
        self.fileControlRecord += self._blockCount
        self.fileControlRecord += self._entryCount
        self.fileControlRecord += self._entryHash
        self.fileControlRecord += self._totalDebitAmount
        self.fileControlRecord += self._totalCreditAmount
        self.fileControlRecord += self.__reserved
        return self.fileControlRecord


class Batch:
    def __init__(self, company_identification_number, dfi_number, service_class):
        self._companyIdentificationNumber = company_identification_number
        self._originatorDFIIdentification = dfi_number
        self._serviceClass = service_class
        self._companyName = ''
        self._batchHeader = ''
        self._totalDebitAmount = 0
        self._totalCreditAmount = 0
        self._entryHash = 0
        self._entryCount = 0
        self.entryRecords = []

    def add_entry(self, transaction_code, routing_number, account_number, amount, identification_number, receiver_name,
                  discretionary_data=''):
        _entry = Entry(transaction_code, routing_number, account_number, amount,
                       identification_number, receiver_name, discretionary_data, self._originatorDFIIdentification)
        self.entryRecords.append(_entry)

    def finalize(self, company_name, discretionary_data, entry_class_code,
                 entry_description, batch_number,
                 service_class=MIXED, description_date=todayWithFormat, effective_entry_date=todayWithFormat):
        self._batchHeader = BatchHeader(company_name, discretionary_data, self._companyIdentificationNumber,
                                        entry_class_code, entry_description, self._originatorDFIIdentification,
                                        batch_number, service_class,
                                        description_date, effective_entry_date)
        for entry in self.entryRecords:
            self._batchHeader.entryRecords.append(entry)
        self._batchHeader.finalize()
        self._totalDebitAmount = self._batchHeader._totalDebitAmount
        self._totalCreditAmount = self._batchHeader._totalCreditAmount
        self._entryHash = self._batchHeader._entryHash
        self._entryCount = self._batchHeader._entryCount


class BatchHeader:
    _recordType = '5'  # ACH Batch Header records are type 5
    __reserved = ''.ljust(3)  # DO NOT MODIFY THIS. It is auto generated by the receiving bank.
    _originatorStatusCode = '1'

    def __init__(self, company_name, discretionary_data, company_identification_number,
                 entry_class_code, entry_description, dfi_number, batch_number, trace_number,
                 service_class=MIXED, description_date=todayWithFormat, effective_entry_date=todayWithFormat):
        self._companyName = str(company_name).ljust(16)
        self._discretionaryData = str(discretionary_data).ljust(20)
        self._companyIdentificationNumber = str(company_identification_number).ljust(10)
        self._entryClassCode = str(entry_class_code).ljust(3)
        self._serviceClass = str(service_class).ljust(3)
        self._entryDescription = str(entry_description).ljust(10)
        self._descriptiveDate = str(description_date).ljust(6)
        self._effectiveEntryDate = str(effective_entry_date).ljust(6)
        self._originatorDFIIdentification = str(dfi_number).ljust(8)
        self._batchNumber = str(batch_number).ljust(7)
        self._batchControlRecord = ''
        self.entryRecords = []
        self._entryCount = len(self.entryRecords)
        self._totalDebitAmount = 0
        self._totalCreditAmount = 0
        self._entryHash = 0
        self.batchHeaderRecord = ''

    def generate(self):
        self.batchHeaderRecord += self._recordType[:1]
        self.batchHeaderRecord += self._serviceClass[:3]
        self.batchHeaderRecord += self._companyName[:16]
        self.batchHeaderRecord += self._discretionaryData[:20]
        self.batchHeaderRecord += self._companyIdentificationNumber[:10]
        self.batchHeaderRecord += self._entryClassCode[:3]
        self.batchHeaderRecord += self._entryDescription[:10]
        self.batchHeaderRecord += self._descriptiveDate[:6]
        self.batchHeaderRecord += self._effectiveEntryDate[:6]
        self.batchHeaderRecord += self.__reserved[:3]
        self.batchHeaderRecord += self._originatorStatusCode[:1]
        self.batchHeaderRecord += self._originatorDFIIdentification[:8]
        self.batchHeaderRecord += self._batchNumber[:7]
        self.batchHeaderRecord += '\n'
        return self.batchHeaderRecord

    def finalize(self):
        self._entryCount = len(self.entryRecords)
        entry_hash = 0
        for entry in self.entryRecords:
            entry.finalize()
            self._entryCount += 1
            if entry._transactionCode in (CHECK_DEBIT, SAVINGS_DEBIT):
                self._totalDebitAmount += float(entry._amount)
            elif entry._transactionCode in (CHECK_DEPOSIT, SAVINGS_DEPOSIT):
                self._totalCreditAmount += float(entry._amount)
            entry_hash += int(entry._routingNumber)
        self._entryHash = str(entry_hash)[-10:]
        self._batchControlRecord = BatchControl(self._entryCount, self._entryHash, self._totalDebitAmount,
                                                self._totalCreditAmount, self._companyName,
                                                self._originatorDFIIdentification, self._batchNumber,
                                                self._serviceClass).generate()

    def add_entry(self, transaction_code, routing_number, account_number, amount, identification_number, receiver_name,
                  discretionary_data=''):
        _entry = Entry(transaction_code, routing_number, account_number, amount,
                       identification_number, receiver_name, discretionary_data, self._originatorDFIIdentification)
        self.entryRecords.append(_entry)


class BatchControl:
    _recordType = '8'  # ACH Batch Control records are type 8
    __authenticationCode = ''.ljust(19)  # DO NOT MODIFY THIS. It needs to be blank.
    __reserved = ''.ljust(6)  # DO NOT MODIFY THIS. It needs to be blank.

    def __init__(self, entry_count, entry_hash, total_debt_amount, total_credit_amount,
                 company_identification_number, dfi_number, batch_number, service_class=MIXED):
        self._serviceClass = str(service_class).ljust(3)
        self._entryCount = str(entry_count).rjust(6, '0')
        self.entryHash = str(entry_hash).ljust(10)
        self._totalDebitAmount = str(total_debt_amount).rjust(12, '0')
        self._totalCreditAmount = str(total_credit_amount).rjust(12, '0')
        self._companyIdentificationNumber = str(company_identification_number).ljust(10)
        self._originatorDFIIdentification = str(dfi_number).ljust(8)
        self._batchNumber = str(batch_number).rjust(7)
        self.batchControlRecord = ''

    def generate(self):
        self.batchControlRecord += self._recordType[:1]
        self.batchControlRecord += self._serviceClass[:3]
        self.batchControlRecord += self._entryCount[:6]
        self.batchControlRecord += self.entryHash[:10]
        self.batchControlRecord += self._totalDebitAmount[:12]
        self.batchControlRecord += self._totalCreditAmount[:12]
        self.batchControlRecord += self._companyIdentificationNumber[:10]
        self.batchControlRecord += self.__authenticationCode[:19]
        self.batchControlRecord += self.__reserved[:6]
        self.batchControlRecord += self._originatorDFIIdentification[:8]
        self.batchControlRecord += self._batchNumber[:7]
        self.batchControlRecord += '\n'
        return self.batchControlRecord[:95]


class Entry:
    _entryNumber = 0
    # The following values are printed:
    _recordType = '6'  # Entry Detail record type is 6.

    def __init__(self, transaction_code, routing_number, account_number,
                 amount, identification_number, receiver_name, discretionary_data, trace_number):
        self._transactionCode = str(transaction_code).ljust(2)
        self._routingNumber = str(routing_number).ljust(8)
        self._accountNumber = str(account_number).ljust(17)
        self._amount = str(amount).rjust(10, '0')
        self._identificationNumber = str(identification_number).ljust(15)
        self._receiverName = str(receiver_name).ljust(22)
        self._discretionaryData = str(discretionary_data).ljust(2)
        self._traceNumber = str(trace_number).ljust(15)
        self._addendaCount = 0
        self.entryRecord = ''
        self.addendaRecords = []
        self._hasAddenda = '0'
        self._entryNumber += 1

    def _trace_number(self):
        trace_number = self._traceNumber + str(self._entryNumber).ljust(7, '0')
        return trace_number

    def _check_digit(self):
        routing_number_list = list(self._routingNumber)
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
        self.entryRecord += self._recordType[:1]
        self.entryRecord += self._transactionCode[:2]
        self.entryRecord += self._routingNumber[:8]
        self.entryRecord += self._check_digit()[:1]
        self.entryRecord += self._accountNumber[:17]
        self.entryRecord += self._amount[:10]
        self.entryRecord += self._identificationNumber[:15]
        self.entryRecord += self._receiverName[:22]
        self.entryRecord += self._discretionaryData[:2]
        self.entryRecord += self._hasAddenda[:1]
        self.entryRecord += self._trace_number()[:15]
        self.entryRecord += '\n'
        return self.entryRecord[:95]

    def finalize(self):
        self._addendaCount = len(self.addendaRecords)

    def add_addenda(self, main_detail, type_code):
        _entryRecordID = str(self._traceNumber)
        _addendaRecord = Addenda(main_detail, type_code, _entryRecordID)
        self.addendaRecords.append(_addendaRecord)
        self._hasAddenda = '1'


class Addenda:
    _recordType = '7'  # Addenda records are type 7

    def __init__(self, main_detail, type_code, entry_record_id):
        self._mainDetail = str(main_detail).ljust(80)
        self._typeCode = str(type_code).ljust(2)
        self._entryRecordID = str(entry_record_id).ljust(7)
        self._addendaSequence = 1
        self.addendaRecord = ''

    def generate(self):
        self.addendaRecord += self._recordType[:1]
        self.addendaRecord += self._typeCode[:2]
        self.addendaRecord += self._mainDetail[:80]
        self.addendaRecord += str(self._addendaSequence).ljust(4)[:4]
        self.addendaRecord += self._entryRecordID[:7]
        self.addendaRecord += '\n'
        self._addendaSequence += 1
        return self.addendaRecord


class ACHFile(object):
    def __init__(self):
        self._batchCount = 0
        self._batchNumber = 0
        self._blockCount = 0
        self._entryCount = 0
        self._entryAddendaCount = 0
        self._entryHash = ''
        self._totalDebitAmount = 0
        self._totalCreditAmount = 0
        self._entryDate = todayWithFormat
        self._fileHeader = ''
        self._fileControlRecord = ''
        self.batchRecords = []
        self.destinationName = ''
        self.originName = ''
        self.referenceCode = ''
        self.batchName = ''
        self.headerDiscretionaryData = ''
        self.entryClassCode = ''
        self.entryDescription = ''
        self.descriptiveDate = todayWithFormat
        self.destinationRoutingNumber = ''
        self.companyIdentificationNumber = ''
        self.footerLines = 0
        self.originID = ''

    def create_header(self):
        self._fileHeader = FileHeader(self.destinationRoutingNumber, self.originID,
                                      self.destinationName, self.originName, self.referenceCode)

    def new_batch(self, dfi_number, entry_description=None,
                  batch_name=None, company_identification_number=None,
                  entry_class_code=None, discretionary_data='', service_class=MIXED):
        if entry_description is None:
            entry_description = self.entryDescription
        if batch_name is None:
            batch_name = self.batchName
        if company_identification_number is None:
            company_identification_number = self.companyIdentificationNumber
        if entry_class_code is None:
            entry_class_code = self.entryClassCode
        self._batchNumber += 1
        new_batch = BatchHeader(batch_name, discretionary_data, company_identification_number,
                                entry_class_code, entry_description, dfi_number,
                                self._batchNumber, service_class, self.descriptiveDate)
        self.batchRecords.append(new_batch)

    def append_batch(self, batch):
        self.batchRecords.append(batch)

    def save(self, file_path):
        self._batchCount = self._batchNumber
        self._blockCount = 2 + (2 * self._batchCount)
        self._entryCount = 0
        self._totalDebitAmount = 0
        self._totalCreditAmount = 0
        entry_hash = 0
        for batch in self.batchRecords:
            batch.finalize()
            self._blockCount += int(batch._entryCount)
            self._entryCount += int(batch._entryCount)
            self._totalDebitAmount += int(batch._totalDebitAmount)
            entry_hash += int(batch._entryHash)
        self._entryHash = str(entry_hash)[-10:]
        self._fileControlRecord = FileControl(self._batchCount, self._blockCount, self._entryCount,
                                              self._entryHash, self._totalDebitAmount, self._totalCreditAmount)
        with open(file_path, 'w+') as ach_file:
            file_header = self._fileHeader.generate()
            ach_file.write(file_header)
            for batch in self.batchRecords:
                batch_header = batch.generate()
                ach_file.write(batch_header)
                for entry in batch.entryRecords:
                    entry_record = entry.generate()
                    ach_file.write(entry_record)
                    for addenda in entry.addendaRecords:
                        addenda_record = addenda.generate()
                        ach_file.write(addenda_record)
                batch_control = batch._batchControlRecord
                ach_file.write(batch_control)
            file_control_record = self._fileControlRecord.generate()
            ach_file.write(file_control_record)

            if self.footerLines > 0:
                line = ''.ljust(94, '9')
                for x in range(0, self.footerLines):
                    ach_file.write(line)
