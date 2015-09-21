# pyACH
A library for creating [NACHA](https://www.nacha.org/rules) payment files with Python 3. [These are used to do wire transfers](https://en.wikipedia.org/wiki/NACHA).   
The other two libraries I've found to do this either weren't implemented correctly, or didn't allow for the same level of granularity that this library does. This allows you to group paments by batch if you have multiple clients that all use the same originating financial institution (bank).     
I chose to use a more object oriented approach than that of the other Python ACH library I found because you are creating an ACH object. Also, I wanted to learn more object oriented Python.  
So far I've tested it with WEB, CCD, PDD records. 

Todo: 
  1. Add JSON parsing.
  2. Support for truly concurrent batch adding.
  3. Test other entry record types.
  
#Documentation  


##How to use:
###1. Create a new file:
    payment_file = ACHFile()
	
###2. Add data to the file:
####2.1 File Header:
	payment_file.destination_routing_number = '01234567'
	payment_file.origin_id = '76543210'
	payment_file.destination_name = 'BANK NAME'
	payment_file.origin_name = 'COMPANY NAME'
	payment_file.reference_code = 'SERVICE' //Optional 8 character field
	payment_file.create_header()
####2.2 Batch Header:
	payment_file.batch_bame = 'SUBCOMPANY NAME' 
	//This should be the same as .originName unless you have multiple company records being sent in one file.
	payment_file.entry_description = 'WATER BILL' //Optional 10 character field
	payment_file.company_identification_number = '14785236'
	payment_file.entry_class_code = 'WEB'
	payment_file.service_class_code = ACHRecordTypes.MIXED
	payment_file.add_batch(dfi_number)
####2.3 Entry Record:
	transaction_code = ACHRecordTypes.CHECK_DEBIT
	payment_type_code = ACHRecordTypes.SINGLE_ENTRY
	payment_file.batch_records[-1].add_entry(transaction_code, payor_routing_number, payor_account_number,
	                                         amount, payor_id, payor_name, discretionary_data=payment_type_code) 
	//This will add to the most recently created batch, 
	//but you can add to any batch record by using its 
	//position in the batch_records list.
	
	addenda_type = ACHRecordTypes.POS
	payment_file.batch_records[-1].entry_records[-1].add_addenda(addenda_type, 'Here's some additional information about the transaction')
	//Addenda records are optional.
																  		
###3. Save it:
	payment_file.save(path_to_save)
	
  
##Concurrency
If you're processing a lot of payments you may find that it's faster to generate 
multiple batches at once and append them to an ACH file once the batches are complete.  
You can do this by generating Batch objects as such:

    batch = Batch(company_identification_number, dfi_number, service_class)
    batch.add_entry(transaction_code, routing_number, account_number, amount, 
    		        identification_number, receiver_name, discretionary_data='')
Then, once you have all the entries you need:

    payment_file.append_batch(batch)
