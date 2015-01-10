# pyACH
A library for creating NACHA payment files with Python 3. These are used to do wire transfers.   
The other two libraries I've found to do this either weren't implemented correctly, or didn't allow fo the same level of granularity that this library does, plus I wanted to learn more object oriented Python.   
I chose to use a more object oriented approach than that of the other Python ACH library I found.  
So far I've only tested it with WEB records, but I plan on testing it with all types at some point. 

Todo: 
  1. Add JSON parsing.
  2. Support for truly concurrent batch adding.
  3. Test other entry record types.
  
#Documentation  


##How to use:
###1. Create a new file:
    paymentFile = ACHFile()
	
###2. Add data to the file:
####2.1 File Header:
	paymentFile.destinationRoutingNumber = '01234567'
	paymentFile.originID = '76543210'
	paymentFile.destinationName = 'BANK NAME'
	paymentFile.originName = 'COMPANY NAME'
	paymentFile.referenceCode = 'SERVICE' //Optional 8 character field
	paymentFile.create_header()
####2.2 Batch Header:
	paymentFile.batchName = 'SUBCOMPANY NAME' 
	//This should be the same as .originName unless you have multiple company records being sent in one file.
	paymentFile.entryDescription = 'WATER BILL' //Optional 10 character field
	paymentFile.companyIdentificationNumber = '14785236'
	paymentFile.entryClassCode = 'WEB'
	paymentFile.serviceClassCode = ACHRecordTypes.MIXED
	paymentFile.add_batch(dfi_number)
####2.3 Entry Record:
	transactionCode = ACHRecordTypes.CHECK_DEBIT
	paymentTypeCode = ACHRecordTypes.SINGLE_ENTRY
	paymentFile.batchRecords[-1].add_entry(transactionCode, payorRoutingNumber, payorAccountNumber,
	                                       amount, payorID, payorName, discretionary_data=paymentTypeCode) 
	//This will add to the most recently created batch, 
	//but you can add to any batch record by using its 
	//position in the batchRecords list.
	
	addendaType = ACHRecordTypes.POS
	paymentFile.batchRecords[-1].entryRecords[-1].add_addenda(addendaType, 'Here's some additional information about the transaction')
	//Addenda records are optional.
																  
####2.4. Other options:
	paymentFile.footerLines = 4 //This adds the specified number of lines of 94 9s to the end of the file.
		
###3. Save it:
	paymentFile.save(path_to_save)
	
  
##Concurrency
If you're processing a lot of payments you may find that it's faster to generate 
multiple batches at once and append them to an ACH file once the batches are complete.  
You can do this by generating Batch objects as such:

    batch = Batch(company_identification_number, dfi_number, service_class)
    batch.add_entry(transaction_code, routing_number, account_number, amount, 
    		        identification_number, receiver_name, discretionary_data='')
Then, once you have all the entries you need:

    paymentFile.append_batch(batch)
