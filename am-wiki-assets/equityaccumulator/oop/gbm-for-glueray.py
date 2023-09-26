#!/usr/bin/env python
# coding: utf-8

# # KIKO equity accumulator prescriptive analytics
# ## find good contract specs that maximise the accounting profit/loss
# ## in a number of future price simulations

# In[1]:


# pip install pandas
import pandas as pd
import numpy as np
import requests


# In[2]:


# This file is edited with jupyter notebook and can be executed in jupyter notebook.

# to execute in EC2 in non-parallel mode:
# change the key exec params, save as gbm.py and run it

# to execute in AWS GLUE RAY in parallel mode:
# change the key exec params, save as gbm.py, run: type gbm.py|awk -f gbm.awk > gbm.ray.py and deploy to aws glue.


# In[3]:


#GLUERAY_UNCOMMENT_BEGIN
import ray
ray.init('auto')
#GLUERAY_UNCOMMENT_END


# ## key execution parameters

# In[4]:


webretrieval = True
verbose = False

quick_for_testing = True
do_plot_example_of_paths = True

if quick_for_testing:
    prescriptive_scenarios = range(3)
    noPaths = 10
else:
    prescriptive_scenarios = range(20)
    noPaths = 2*252

noFutprices = 2*252
#GLUERAY_DOCOMMENT_BEGIN
#logger_url = 'http://am1:ampwd239@127.0.0.1:5984/logdb'
#bsaveChartsToFile = True # charts will be displayed and also saved as PNG 
#GLUERAY_DOCOMMENT_END
#GLUERAY_UNCOMMENT_BEGIN
logger_url = 'http://am1:ampwd239@ip-172-31-29-155.eu-west-1.compute.internal:5984/logdb'
logger_url = 'http://am1:ampwd239@ec2-54-246-150-66.eu-west-1.compute.amazonaws.com:5984/logdb'
bsaveChartsToFile = False
#GLUERAY_UNCOMMENT_END

# FS
folder = r'M:\DEV\github__a_moscatelli\repositories\home\am-wiki-assets\equityaccumulator'+'\\'
hist_csv_filename = folder + 'JPM.csv'
contract_yml_filename = folder + 'contract.yml'

# WEB
if webretrieval:
    urlpath='https://raw.githubusercontent.com/a-moscatelli/home/main/am-wiki-assets/equityaccumulator/'
    hist_csv_filename = urlpath + 'JPM.csv'
    contract_yml_url = urlpath + 'contract.yml'




summary = {}
def print_summary():
    # https://stackoverflow.com/questions/18193205/list-comprehension-returning-values-plus-none-none-none-why
    devnull=[ print(kk,'=>',summary[kk]) for kk in summary.keys()] 


# ## step 1.1 - loading the historical data

# In[5]:


class AccumulatorDescriptive:
    
    hdf = None
    stats = None
    hist_csv_filename = None
    
    #def __init__(self):
        #pass
    
    def load_past(self,hist_csv_filename):
        self.hist_csv_filename = hist_csv_filename
        histcolname = 'Date'
        filedateformat = '%Y-%m-%d'
        hdf = pd.read_csv(hist_csv_filename, index_col=histcolname)
            #parse_dates=[histcolname],
            #date_parser=lambda x: datetime.strptime(x,filedateformat),
        self.hdf = hdf.rename(columns={'Adj Close': 'AdjClose'})
        self.__add_returns()
        self.__get_ret_stats()
        
    def __add_returns(self):
        AdjClose = 'AdjClose'
        df=self.hdf
        df['LagAdjClose'] = df[AdjClose].shift(1)
        df['DailyLogRet'] = np.log(df[AdjClose] / df['LagAdjClose'])
        self.hdf = df
        
    def __get_ret_stats(self):
        DailyLogRet = 'DailyLogRet'
        df = self.hdf
        sigma = df[DailyLogRet].std()
        mu = df[DailyLogRet].mean()
        cnt = df[DailyLogRet].count()
        lastclose = df.AdjClose.iloc[-1]
        self.stats = {'sigma':sigma,'mu':mu,'dretCount':cnt,'lastclose':lastclose,'lastdate':df.index[-1]}
        
    def get_past1(self):
        # 1-dim array = just the prices
        return self.hdf.AdjClose.values # or, self.hdf.AdjClose.to_numpy()
    
    def get_past2(self):
        # dataframe = date index and prices
        return self.hdf.AdjClose
    
    def info(self):
        print('hist_csv_filename:',self.hist_csv_filename)
        print('hist_df_shape:',self.hdf.shape)
        print('hist_firstdt:',self.hdf.index[0])
        print('hist_lastdt:',self.hdf.index[-1])
        print('hist_profile:',self.stats)
        print('dfshape:',self.hdf.shape)
        print('stats:',self.stats)

# class AccumulatorDescriptive    


# *execution*

# In[6]:


acchist = AccumulatorDescriptive()
acchist.load_past(hist_csv_filename)
acchist.info()


# ## step 1.2 - profiling the historical data

# In[7]:


acchist.hdf.DailyLogRet.describe()


# ## step 1.3 - computing the future price paths

# In[8]:


class AccumulatorPredictive:
    
    stats = None # # {'sigma':sigma,'mu':mu,'dretCount':cnt,'lastclose':lastclose}
    rpath0 = None
    contract_spec = None
    contract_fname = None
    days = -1
    noPaths = -1
    fut_firstdt = None
    fut_lastdt = None
    
    def __init__(self,stats_dict):
        self.stats = stats_dict
        assert max(True,False)==True and min(True,False)==False
        # ... as a verification of any platform-dependent logic
        
    def __get_futpath(self,lastclose,drift,vol,ndays):
        # private
        n = ndays # self.days    #n = 252
        dt = 0.1
        x0 = lastclose
        mu = drift # self.stats['mu'] # 
        sigma = vol # 
        sz=1
        x = np.exp(
            (mu - sigma ** 2 / 2) * dt
            +
            sigma * np.random.normal(0, np.sqrt(dt), size=(sz, n)).T
        )

        x = np.vstack([np.ones(sz), x])
        x = x0 * x.cumprod(axis=0)
        rp = x[:,0]
        AdjCloseFuturesPrices = x[:,0]
        
        debug=False
        if debug:
            df = pd.DataFrame({'AdjClose':AdjCloseFuturesPrices},index=None) # , index=rows, columns=columns) # was px
            #... df = add_columns(df,'AdjClose')  # was px
            ss = getstats(df,'DailyLogRet')
            if verbose: print('path stats:',ss)
        
        delete_the_first = True
        # the first is the last of the provided historical prices
        assert len(AdjCloseFuturesPrices) == n + 1
        if delete_the_first:
            AdjCloseFuturesPrices = np.delete(AdjCloseFuturesPrices, 0)
            # xfut[0] is going to be = xpast[-1], hence this removal.    
        assert len(AdjCloseFuturesPrices) == n
        return AdjCloseFuturesPrices

        #math.sqrt(250)

    def buildpath(self,days):
        assert days > 0
        self.days = days
        self.rpath0 = self.__get_futpath(self.stats['lastclose'],self.stats['mu'],self.stats['sigma'],days)

    def load_contract_spec_dict(self,contract_dict,contract_fname):
        self.contract_fname = contract_fname
        self.contract_spec = contract_dict
        
    def load_contract_spec(self,contract_fname):
        assert False # deprecated
        self.contract_fname = contract_fname
        with open(contract_fname, 'r') as file:
            contract_spec = yaml.safe_load(file)
            #    contract_spec['dates']['startdate'] =
                # datetime.strptime(contract_spec['dates']['startdate'],   contract_spec['dates']['dateformat'])
            #    contract_spec['dates']['enddate']   = 
                # datetime.strptime(contract_spec['dates']['enddate'],     contract_spec['dates']['dateformat'])
            # 2022-07-08
            #del contract_spec['dates']['dateformat']
            self.contract_spec = contract_spec
            
    def __getnextdt_str(self,prevdt_str,considerPublicHolidays):
        # private
        assert prevdt_str.__class__.__name__ == 'str'
        prevdt = datetime.strptime(prevdt_str,"%Y-%m-%d")
        dtx = self.__getnextdt(prevdt,considerPublicHolidays)
        return datetime.strftime(dtx,"%Y-%m-%d")

    def __getnextdt(self,prevdt,considerPublicHolidays):
        # private
        assert not considerPublicHolidays
        assert prevdt.__class__.__name__ == 'datetime'
        dow_eur=prevdt.strftime("%a")
        #print(lastdt,dow_eur)
        offset=1
        if dow_eur == 'Fri': offset=3
        if dow_eur == 'Sat': offset=2
        nextdt = prevdt + timedelta(days=offset)
        return nextdt
    
    def __get_future_dates(self):
        #lastdate=yh.index[-1]
        futdt = []
        curdt = self.stats['lastdate'] #lastdate
        futpath0 = self.rpath0 # self.rpath[0] # rpath[path]
        for px in futpath0:
            curdt=self.__getnextdt_str(curdt,False)
            futdt.append(curdt)
            #print(px)
            #pass
        assert len(futdt) == len(futpath0) # len(rpath[path])
        assert self.stats['lastdate'] != futdt[0]
        self.fut_firstdt = futdt[0]
        self.fut_lastdt = futdt[-1]
        return futdt

    def get_past_n_fut1(self,pastpx):
        # one-dim arrays = just the prices
        futpx = self.rpath0
        return np.concatenate([pastpx,futpx])

    def __get_past_n_fut2(self,pastdf):
        # dataframes = date index and prices
        futdt = self.__get_future_dates()
        futfd = pd.DataFrame({'AdjClose':self.rpath0},index=futdt)
        #yh = pastpx # pd.DataFrame({'AdjClose':pastpx},index=futdt)
        if pastdf is None: return futfd
        return pd.concat([pastdf,futfd])

    def compute1_noncumul(self,pastdf):
        hdf_df = self.__get_past_n_fut2(pastdf)
        contract_spec = self.contract_spec
        
        contract_startdate_is_included_in_futpath = contract_spec['dates']['startdate'] >= self.fut_firstdt
        contract_enddate_is_included_in_futpath = contract_spec['dates']['enddate'] <= self.fut_lastdt
        assert contract_startdate_is_included_in_futpath
        assert contract_enddate_is_included_in_futpath
        
        hdf_df['live'] = hdf_df.apply(lambda row:  contract_spec['dates']['startdate'] <= row.name <= contract_spec['dates']['enddate'], axis=1)
        hdf_df['KI'] = hdf_df.apply(lambda row:  row.live and eval(contract_spec['knock-in'],{'row':row}), axis=1).cummax()
        # the input of cummax is a df column having true when the KI condition is met.
        # cummax() keeps confirming True in the future once met. cummax = carryover of True.
        hdf_df['KO'] = hdf_df.apply(lambda row:  row.KI and eval(contract_spec['knock-out'],{'row':row}), axis=1).cummax()
        hdf_df['accumulation'] = hdf_df['KI'] & ~hdf_df['KO']
        # bitwise is inside the KI zone and not inside the KO zone
        return hdf_df

    def compute2_cumul(self,hdf,BQ,SQ):
        contract_spec = self.contract_spec
        hdf.insert(0, 'SN', range(0, 0 + len(hdf)))

        hdf['BQty']  = hdf.apply(lambda row: row.accumulation and eval(contract_spec['buy']['qty'],  {'row':row, 'math':math,'hist':self.hist,'H':hdf,'T':row.name,'BQ':BQ,'SQ':SQ}), axis=1)
        hdf['BAt']   = hdf.apply(lambda row: row.accumulation and eval(contract_spec['buy']['at'],   {'row':row, 'math':math,'hist':self.hist,'H':hdf,'T':row.name}), axis=1)
        hdf['BWhen'] = hdf.apply(lambda row: row.accumulation and eval(contract_spec['buy']['when'], {'row':row, 'math':math,'hist':self.hist,'H':hdf,'T':row.name}), axis=1)
        hdf['SQty']  = hdf.apply(lambda row: row.accumulation and eval(contract_spec['sell']['qty'], {'row':row, 'math':math,'hist':self.hist,'H':hdf,'T':row.name,'BQ':BQ,'SQ':SQ}), axis=1)
        hdf['SAt']   = hdf.apply(lambda row: row.accumulation and eval(contract_spec['sell']['at'],  {'row':row, 'math':math,'hist':self.hist,'H':hdf,'T':row.name}), axis=1)
        hdf['SWhen'] = hdf.apply(lambda row: row.accumulation and eval(contract_spec['sell']['when'],{'row':row, 'math':math,'hist':self.hist,'H':hdf,'T':row.name}), axis=1)
        #cashflow
        hdf['BCF']   = hdf.apply(lambda row: row.accumulation and row.BWhen and - (row.BQty * row.BAt),axis=1)
        hdf['SCF']   = hdf.apply(lambda row: row.accumulation and row.SWhen and + (row.SQty * row.SAt),axis=1)
        #cumul
        hdf['CumQty']= hdf.apply(lambda row: row.BWhen and row.BQty - row.SWhen and row.SQty , axis=1).cumsum()
        hdf['CumCF'] = hdf.apply(lambda row: row.BCF + row.SCF, axis=1).cumsum()
        return hdf

    def hist(self,field,date,dayoffset,hdf):
        #global hdf
        # historical data lookup - relative to T
        assert dayoffset <= 0
        # date is str
        #date_ = datetime.strptime(date,"%Y-%m-%d")
        #date2 = date + timedelta(days=dayoffset)	# may not be included in the df
        #print('hist:',date,field,dayoffset,date2)
        ret = hdf.shift(dayoffset).at[date,field]
        if not ret: ret=0
        return ret

    def get_lastCumCF(self,scn,pastdf):

        BQ = scn[0]
        SQ = scn[1]

        rpathx = self.rpath0
        if verbose: print('min/max/avg path px',min(rpathx),max(rpathx),statistics.mean(rpathx))

        # simulate accumulation

        fulldf = self.compute1_noncumul(pastdf)

        accumulation_occurs = fulldf.loc[fulldf.accumulation].shape[0] > 0

        if accumulation_occurs:
            acc_a = fulldf.loc[fulldf.accumulation].head(1).index.values[0]
            acc_z = fulldf.loc[fulldf.accumulation].tail(1).index.values[0]
            if verbose: print('Accumulation','begins on:',acc_a,'ends on',acc_z) # .loc[hdf.df['accumulation']==True].idxmin())
            # .loc[hdf.df.accumulation==True].idxmax())
        else:
            if verbose: print('Accumulation begins/ends: NEVER')

        fulldf = self.compute2_cumul(fulldf,BQ,SQ)
        # hdf.df
        lastCumCF=fulldf["CumCF"].iloc[-1]
        avgCumCF=fulldf["CumCF"].mean()
        if verbose: print('ipath',ipath,'CumCF',lastCumCF,'avgCumCF',avgCumCF)
        #lastCumCF_array.append(lastCumCF)

        if False:
            plt.plot(fulldf["CumCF"]) #, df["Y"])
            plt.show()

        return lastCumCF # lastCumCF_array

    def info(self):
        print('days:',self.days)
        print('noPaths:',self.noPaths)
        print('contract_spec:',self.contract_spec)
        print('contract_fname:',self.contract_fname)
        print('hist_stats:',self.stats)
        print('fut_firstdt:',self.fut_firstdt)
        print('fut_lastdt:',self.fut_lastdt)
        


# In[9]:


import matplotlib.pyplot as plt
#from scipy.stats import norm
#import math


# *execution*

# In[10]:


from datetime import datetime
# ... this is only for logging


# In[11]:


# BTW:

if do_plot_example_of_paths:
    
    #noPaths = 252
    summary['exec_example_gbm_start'] = datetime.now()
    xpast = acchist.get_past1() # = yh.AdjClose.to_numpy()
    # building the hist+fut paths = the inputs of the pricer
    accpred = AccumulatorPredictive(acchist.stats)
    fullpath = []
    for ipath in range(noPaths):
        accpred.buildpath(noFutprices)
        full = accpred.get_past_n_fut1(xpast)
        fullpath.append(full)
    summary['exec_example_gbm_end__'] = datetime.now()
    
    for ipath in range(noPaths):
        plt.plot(fullpath[ipath])
        plt.title("Realizations of Geometric Brownian Motion")
    
    if bsaveChartsToFile:
        plt.savefig('gbm_paths_example.png')
    else:
        plt.show()


# ## step 2.0 - telemetry (couchdb)

# In[12]:


import socket

class Couchdbcli:
    #urlz = 'http://127.0.0.1:5984/'
    urlc = 'http://am1:ampwd239@127.0.0.1:5984/logdb'
    #logdb = 'logdb'
    partitionid = 'tag'
    def __init__(self,urlc_):
        self.urlc=urlc_
        #devnull = self.getz()
    def createdb(self,predelete):
        if predelete:
            #DELETE /{db}
            print('predelete',predelete)
            response = requests.delete(self.urlc) # , data={'key':'value'})
            print('predelete',predelete,'response.status_code',response.status_code)
        response = requests.put(self.urlc) # , data={'key':'value'})        
        return (response.status_code,response.json())
    def getnow__(self):
        #Local to ISO 8601:
        localtm = datetime.now().isoformat() # 2020-03-20T14:28:23.382748
        # UTC to ISO 8601:
        utctm = datetime.utcnow().isoformat() # 2020-03-20T01:30:08.180856
        return utctm
    def log(self,tag,bodydict):
        payload = {'datetime':self.getnow__(),self.partitionid:tag,'body':bodydict,'hostname':socket.gethostname()}
        response = requests.post(self.urlc, json=payload)
        return (response.status_code,response.json())
    def getall(self):
        payload = {"selector":{},
                   "fields": [ "datetime",  self.partitionid ]
                   # , "sort": [{"datetime": "asc"}]
                  }
        response = requests.post(self.urlc+'/_find', json=payload)
        return response.json()['docs']
    
logger = Couchdbcli(logger_url)


# ## step 2.1 - loading pricing specs

# In[13]:


random_seed = 1 
np.random.seed(random_seed)
print('random_seed =',random_seed)


# In[14]:


import yaml  # pip install pyyaml
from datetime import datetime, timedelta


# ## step 2.2 - prescriptive and pricing loop

# In[15]:


import math
import statistics


# In[16]:


print_summary()


# In[17]:


class AccumulatorPrescriptive():
    
    prsdata = None
    
    def __init__(self):
        self.prsdata = pd.DataFrame(None, columns = ["BQ", "SQ","P_Loss","MaxCumCF","MinCumCF"], index=None)
    
    def build_scenario(self):
        BQ = np.random.randint(1, 10) # (inclusive,exclusive)
        SQ = np.random.randint(1, 10) # (inclusive,exclusive)
        return (BQ,SQ)

    def log(self,inargs,outargs):
        BQ = inargs[0]
        SQ = inargs[1]
        self.prsdata.loc[len(self.prsdata)] = [BQ,SQ] + outargs


# In[18]:


summary['exec_prescriptive_loop_start'] = datetime.now()


# In[19]:


#noFutprices = 2*252


def get_contract_dict(fromweb):
    if not fromweb:
        with open(contract_yml_filename, 'r') as cfile:
            contract_dict = yaml.safe_load(cfile)
    else:
        txt = requests.get(contract_yml_url, allow_redirects=True).content
        contract_dict = yaml.safe_load(txt)
    return contract_dict
        
contract_dict = get_contract_dict(webretrieval)

sample_histog_data = None # will be set to the last scn_lastCumCF_array
sample_histog_data_scn = None

# By adding the `@ray.remote` decorator, a regular Python function
# becomes a Ray remote function.
#GLUERAY_UNCOMMENT_BEGIN
@ray.remote
#GLUERAY_UNCOMMENT_END
def get_remote_task_result(acchist_stats_dict,contract_dict,noFutprices,scn,pxpath,tag,logger):
    logger.log(tag,{'scn':scn,'pxpath':int(pxpath)})
    accpred = AccumulatorPredictive(acchist_stats_dict)
    accpred.load_contract_spec_dict(contract_dict,'unknown contract fname')
    accpred.buildpath(noFutprices)
    pastdf = None # do not use the past prices as in: pastdf = acchist.get_past2()
    lastCumCF = accpred.get_lastCumCF(scn,pastdf)
    return lastCumCF

accpres = AccumulatorPrescriptive()

for prs in prescriptive_scenarios:
    scn = accpres.build_scenario()
    print('time:',datetime.now().strftime('%Y-%m-%d-%H:%M:%S'),'going to start pricing '+str(noPaths)+' '+str(noFutprices)+'-day paths with prescriptive scenario',prs,'(BQ,SQ)',scn)
    
    # MAP
    
    #parallel template:
    #tasks = [f.remote(i) for i in range(1,9)]
    #ray.get(tasks) 
    
    #GLUERAY_UNCOMMENT_BEGIN

    if False:
        scn_lastCumCF_array = [ ray.get(get_remote_task_result.remote(acchist.stats,contract_dict,noFutprices,scn,pxpath,'wrong-par',logger)) for pxpath in range(noPaths) ]
    if False:
        scn_lastCumCF_array_futs = [ get_remote_task_result.remote(acchist.stats,contract_dict,noFutprices,scn,pxpath,'par',logger) for pxpath in range(noPaths) ]
        scn_lastCumCF_array = [ ray.get(fut) for fut in scn_lastCumCF_array_futs ]
    if True:
        scn_lastCumCF_array_futs = [ get_remote_task_result.remote(acchist.stats,contract_dict,noFutprices,scn,pxpath,'par',logger) for pxpath in range(noPaths) ]
        scn_lastCumCF_array = ray.get(scn_lastCumCF_array_futs)
    
    #GLUERAY_UNCOMMENT_END
    
    #GLUERAY_DOCOMMENT_BEGIN
#    scn_lastCumCF_array = [ get_remote_task_result(acchist.stats,contract_dict,noFutprices,scn,pxpath,'nopar',logger) for pxpath in range(noPaths) ]
    #GLUERAY_DOCOMMENT_END
    
    # REDUCE
    
    sample_histog_data = scn_lastCumCF_array
    sample_histog_data_scn = prs # scn
    
    Ploss = len(list(filter(lambda cumcf: cumcf < 0, scn_lastCumCF_array))) / len(scn_lastCumCF_array)
    max_lastCumCF_array = max(scn_lastCumCF_array)
    min_lastCumCF_array = min(scn_lastCumCF_array)
    accpres.log( scn, [Ploss, max_lastCumCF_array, min_lastCumCF_array] )


# In[20]:


summary['exec_prescriptive_loop_end__'] = datetime.now()


# In[21]:


plt.hist(sample_histog_data, density=False, bins=30)
plt.title("Distribution of Accounting P/L (scn "+str(sample_histog_data_scn)+")")
    #None # to prevent non-required output
if bsaveChartsToFile:
    plt.savefig('final_pl_hist.png')
else:
    plt.show()    


# In[22]:


print_summary()


# In[27]:


import json
contract_spec=get_contract_dict(webretrieval)
print(json.dumps(contract_spec, indent=4))


# In[24]:


prsdata = accpres.prsdata
prsdata


# ## contract parameters (BuyQty,SellQty) that resulted in the lowest Probability of Loss

# In[25]:


print(prsdata[prsdata.P_Loss == prsdata.P_Loss.min()])
# BQ   SQ  P_Loss       MaxCumCF  MinCumCF
# 0   2.0  4.0     0.0   50121.170219       0.0
# 2   3.0  9.0     0.0  132204.524247       0.0
# 5   1.0  7.0     0.0  120098.533306       0.0
# 15  3.0  7.0     0.0   94189.344968       0.0
# 16  3.0  9.0     0.0  132204.524247       0.0


# ### summary plot

# In[26]:


ax = prsdata.plot(kind='scatter',x='BQ',y='SQ',c='P_Loss',title='PLoss(BQ,SQ)')
ax.set(xlabel="buy qty", ylabel="sell qty")
if bsaveChartsToFile:
    fig = ax.get_figure()
    fig.savefig('prescriptive_scatter.png')

#GLUERAY_DOCOMMENT_BEGIN
#ax.show()
#GLUERAY_DOCOMMENT_END


# ## END
