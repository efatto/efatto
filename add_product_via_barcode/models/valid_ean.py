from stdnum import ean

def valid_barcode(ean13):
		if len(ean13) == 13:
			return ean.is_valid(ean13)
		elif len(ean13) == 12:
			hashlist = list(ean13)
			hashlist.insert(0, '0')
			number = ''.join(hashlist)
			return ean.is_valid(number)