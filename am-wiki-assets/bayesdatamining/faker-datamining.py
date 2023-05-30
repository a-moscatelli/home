import csv
from faker import Faker
from datetime import date, timedelta

output_rows = 500000

faker = Faker()
today = date.today()

faker_domain_finproducts = ['fx spot', 'fx swap', 'fx fwd', 'fx futures']
faker_domain_forexcuts = ['NYC1000', 'TKY1500', 'ECB1415']	# bei 0915 bei 1500, bfix 1500, bfix 3pm, ldn 1300, ldn 1500 xau, syd 1500

output_csv = '.'.join(['fake-pnl-report',today.strftime('%Y-%m-%d'),'csv'])

print('writing file:',output_csv)

with open(output_csv, 'w', newline='') as file:
	fieldnames =	[
							'id', 'trade_date', 'exp_date', 'trader',  'trade_ccy', 'product', 'disc_curve', 'fx_cut', 'market', 'PnL_ccy', 
							'delim', 
							'uPnL', 'rPnL', 'PnL'
						]
	writer = csv.DictWriter(file, fieldnames=fieldnames)
	writer.writeheader()
	for r in range(output_rows):

		if r%1000 == 0:
			print('writing row:',r)

		# preparation of values used in multiple output fields:
		common1 = today + timedelta( days = faker.random_int(-10, 10))
		common2 = faker.country_code() # .country()
		pnl1realized = round(faker.random_int(-10*1000*1000, +10*1000*1000) * 0.9876,2)
		pnl2unrealized = round(faker.random_int(-10*1000*1000, +10*1000*1000) * 0.9876,2)
		# also available: faker.pydecimal(left_digits=2, right_digits=None, positive=False, min_value=None, max_value=None)

		ccy1 = 'USD'
		ccy2 = faker.currency_code()
		if ccy2 == 'USD':
			ccy2 = 'EUR'
		if ccy2 in "EUR>GBP>AUD>NZD".split(">"):
			# https://forextraininggroup.com/an-overview-of-the-major-forex-currency-pairs/
			# pecking order : EUR > GBP > AUD > NZD > USD > CHF > JPY
			newccy1= ccy2
			newccy2= ccy1
			ccy1 = newccy1
			ccy2 = newccy2

		writer.writerow({
			'id' : r,
			'trade_date': common1,
			'exp_date': common1 + timedelta( days = faker.random_int(0, 50)),
			'trader': faker.name(),
			'uPnL': pnl2unrealized,
			'rPnL': pnl1realized,
			'PnL': round(pnl1realized+pnl2unrealized,2),
			'PnL_ccy': ccy1,
			'trade_ccy': ccy1+ccy2,
			'product': faker.words(1,False,faker_domain_finproducts)[0],
			'disc_curve': ccy1+ccy2+"-"+common2,
			'fx_cut': faker.words(1,False,faker_domain_forexcuts)[0],
			'market': common2,
			'delim' : ':'
		})
