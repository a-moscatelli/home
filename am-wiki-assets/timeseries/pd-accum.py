# M:\DEV\A-MOSCATELLI-WIKI\accumulator>python pd-accum.py jpm.csv jpm.out.csv contract.yml

# c:\NotBackedUp\Python39_64\python.exe
# C:\NotBackedUp\_MY_SOFTWARE_STUFF\equity>c:\NotBackedUp\Python39_64\python.exe simul.py JPM.csv JPM.out.csv contract1.yml

import pandas as pd
import yaml  # pip install pyyaml

import sys
from datetime import datetime, timedelta

assert len(sys.argv) == 1+3, "syntax: " + sys.argv + " in_csv_filename.csv out_csv_filename.csv contract_specs_filename.yml"
this_script, in_csv_filename, out_csv_filename, contract = sys.argv

# read contract.yml

with open(contract, 'r') as file:
	contract_spec = yaml.safe_load(file)
	contract_spec['dates']['startdate'] = datetime.strptime(contract_spec['dates']['startdate'],   contract_spec['dates']['dateformat'])
	contract_spec['dates']['enddate']   = datetime.strptime(contract_spec['dates']['enddate'],     contract_spec['dates']['dateformat'])
	# 2022-07-08
	del contract_spec['dates']['dateformat']
	#print(contract_spec)

#dateparse = lambda x: datetime.strptime(x, '%d/%m/%Y')
#dfi = pd.read_csv(in_csv_filename, parse_dates=['Date'], date_parser=dateparse) # , index_col='Date')
# ok: print(dfi.dtypes)

#print('dates, initial:',dfi.shape[0])

#dff = dfi[dfi.apply(lambda row: filter1(row), axis=1)].copy()
#print('dates, after','acceptance_criteria_start',dff.shape[0])
#dff=dfi

class Hdf:
    df = None
    def _dbg(self,trace):
        print('count of dates after','<'+trace+'>',':',self.df.shape[0])
    def __init__(self, hist_csv_filename,histcolname,filedateformat):
        self.df = pd.read_csv(
                    hist_csv_filename,
                    parse_dates=[histcolname],
                    date_parser=lambda x: datetime.strptime(x,filedateformat),
                    index_col=histcolname)
        self._dbg('init')
        # https://www.dataquest.io/blog/tutorial-time-series-analysis-with-pandas/ follows the same steps
        False and print(self.df.dtypes)
		
    def withSignal(self,colname,lambdasignal,activation):
        assert False
        assert activation in ['up','down']
        self.df[colname] = self.df.apply(lambda row: lambdasignal(row), axis=1).copy()
        fdf = self.df[self.df[colname]]
        if fdf.shape[0]>=0:
            activation_index = fdf.index[0]
            print('activation_index',activation_index)
            if activation=='up':
                self.df[colname] = self.df.apply(lambda row: row.name >= activation_index, axis=1).copy()
            if activation=='down':
                self.df[colname] = self.df.apply(lambda row: row.name <= activation_index, axis=1).copy()
        self._dbg(colname)
        return self



print('start')
hdf = Hdf(in_csv_filename,'Date',contract_spec['dates']['filedateformat'])

def hist(field,date,dayoffset):
	assert dayoffset <= 0
	date2 = date + timedelta(days=dayoffset)	# may not be included in the df
	#print('hist:',date,field,dayoffset,date2)
	ret = hdf.df.shift(dayoffset).at[date,field]
	#print('shifted hist:',hdf.df.shift(dayoffset).loc[date])
	#ret = hdf.df.at[date2,field]
	#print('ret:',ret)
	if not ret: ret=0
	return ret

assert max(True,False)==True and min(True,False)==False
import math

hdf.df['live'] =	hdf.df.apply(lambda row:  contract_spec['dates']['startdate'] <= row.name <= contract_spec['dates']['enddate'],	axis=1)
hdf.df['KI'] =		hdf.df.apply(lambda row:  row.live and eval(contract_spec['knock-in'],{'row':row}),	axis=1).cummax()
# the input of cummax is a df column having true when the KI condition is met. cummax() keeps confirming True in the future once met. cummax = carryover of True.
hdf.df['KO'] =	hdf.df.apply(lambda row:  row.KI and eval(contract_spec['knock-out'],{'row':row}),	axis=1).cummax()
hdf.df['accumulation'] = hdf.df['KI'] & ~hdf.df['KO']
# bitwise is inside the KI zone and not inside the KO zone

print('accumulation start:',hdf.df.loc[hdf.df.accumulation].head(1).index.values[0])	#	.loc[hdf.df['accumulation']==True].idxmin())
print('accumulation stop:',hdf.df.loc[hdf.df.accumulation].tail(1).index.values[0])		#.loc[hdf.df.accumulation==True].idxmax())

if False:
	hdf.df['BQty'] = False
	hdf.df['BCF'] = False
	hdf.df['SQty'] = False
	hdf.df['SCF'] = False
	hdf.df['CumQty'] = False
	hdf.df['CumCF'] = False

hdf.df.insert(0, 'SN', range(0, 0 + len(hdf.df)))

hdf.df['BQty'] = hdf.df.apply(	lambda row: row.accumulation and eval(contract_spec['buy']['qty'],		{'row':row, 'math':math,'hist':hist,'T':row.name}),	axis=1)
hdf.df['BAt'] = hdf.df.apply(	lambda row: row.accumulation and eval(contract_spec['buy']['at'],		{'row':row, 'math':math,'hist':hist,'T':row.name}),	axis=1)
hdf.df['BWhen'] = hdf.df.apply(	lambda row: row.accumulation and eval(contract_spec['buy']['when'],	{'row':row, 'math':math,'hist':hist,'T':row.name}),	axis=1)
hdf.df['SQty'] = hdf.df.apply(	lambda row: row.accumulation and eval(contract_spec['sell']['qty'],		{'row':row, 'math':math,'hist':hist,'T':row.name}),	axis=1)
hdf.df['SAt'] = hdf.df.apply(	lambda row: row.accumulation and eval(contract_spec['sell']['at'],		{'row':row, 'math':math,'hist':hist,'T':row.name}),	axis=1)
hdf.df['SWhen'] = hdf.df.apply(	lambda row: row.accumulation and eval(contract_spec['sell']['when'],	{'row':row, 'math':math,'hist':hist,'T':row.name}),	axis=1)
#cashflow
hdf.df['BCF'] = hdf.df.apply(	lambda row: row.accumulation and row.BWhen and - (row.BQty * row.BAt),		axis=1)
hdf.df['SCF'] = hdf.df.apply(	lambda row: row.accumulation and row.SWhen and + (row.SQty * row.SAt),		axis=1)
#cumul
hdf.df['CumQty'] = hdf.df.apply(	lambda row: row.BWhen and row.BQty - row.SWhen and row.SQty , axis=1).cumsum()
hdf.df['CumCF'] = hdf.df.apply(	lambda row: row.BCF + row.SCF, axis=1).cumsum()

hdf.df.to_csv(out_csv_filename,index=True)
print('file',out_csv_filename,'is written.')
print('done.')

