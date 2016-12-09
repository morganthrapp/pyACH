FILE_HEADER_LENGTHS = {'RECORD TYPE CODE': 1,
                       'PRIORITY CODE': 2,
                       'IMMEDIATE DESTINATION': 10,
                       'IMMEDIATE ORIGIN': 10,
                       'FILE CREATION DATE': 6,
                       'FILE CREATION TIME': 4,
                       'FILE ID MODIFIER': 1,
                       'RECORD SIZE': 3,
                       'BLOCKING FACTOR': 2,
                       'FORMAT CODE': 1,
                       'IMMEDIATE DESTINATION NAME': 23,
                       'IMMEDIATE ORIGIN NAME': 23,
                       'REFERENCE CODE': 8
                       }

FILE_CONTROL_LENGTHS = {'RECORD TYPE CODE': 1,
                        'BATCH COUNT': 6,
                        'BLOCK COUNT': 6,
                        'DETAIL COUNT': 8,
                        'ENTRY HASH': 10,
                        'TOTAL DEBIT AMOUNT': 12,
                        'TOTAL CREDIT AMOUNT': 12,
                        'RESERVED': 39
                        }

BATCH_HEADER_LENGTHS = {'RECORD TYPE CODE': 1,
                        'SERVICE CLASS CODE': 3,
                        'COMPANY NAME': 16,
                        'DISCRETIONARY DATA': 20,
                        'COMPANY IDENTIFICATION': 10,
                        'ENTRY CLASS CODE': 3,
                        'ENTRY DESCRIPTION': 10,
                        'DESCRIPTIVE DATE': 6,
                        'EFFECTIVE ENTRY DATE': 6,
                        'SETTLEMENT DATE': 3,
                        'ORIGINATOR STATUS CODE': 1,
                        'ORIGINATING DFI IDENTIFICATION': 8,
                        'BATCH NUMBER': 7
                        }

BATCH_CONTROL_LENGTHS = {'RECORD TYPE CODE': 1,
                         'SERVICE CLASS CODE': 3,
                         'DETAIL COUNT': 6,
                         'ENTRY HASH': 10,
                         'TOTAL DEBIT AMOUNT': 12,
                         'TOTAL CREDIT AMOUNT': 12,
                         'COMPANY IDENTIFICATION': 10,
                         'AUTHENTICATION CODE': 19,
                         'RESERVED': 6,
                         'ORIGINATING DFI IDENTIFICATION': 8,
                         'BATCH NUMBER': 7
                         }

ENTRY_LENGTHS = {'RECORD TYPE CODE': 1,
                 'TRANSACTION CODE': 2,
                 'RECEIVING DFI ID': 9,
                 'CHECK DIGIT': 1,
                 'DFI ACCOUNT NUMBER': 17,
                 'DOLLAR AMOUNT': 10,
                 'INDIVIDUAL IDENTIFICATION': 15,
                 'INDIVIDUAL NAME': 22,
                 'DISCRETIONARY DATA': 2,
                 'ADDENDA': 1,
                 'TRACE NUMBER': 15
                 }

ADDENDA_LENGTHS = {'RECORD TYPE': 1,
                   'TYPE CODE': 2,
                   'MAIN DETAIL': 80,
                   'SEQUENCE': 4,
                   'ENTRY RECORD ID': 7
                   }
