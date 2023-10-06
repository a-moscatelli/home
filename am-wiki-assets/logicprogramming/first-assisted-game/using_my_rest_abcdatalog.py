#!/usr/bin/env python
# coding: utf-8

# In[1]:


# alternatives to this python client:
# - the online service: https://datalog.db.in.tum.de/
# - the desktop GUI. Just run: java -jar AbcDatalog-0.6.0.jar


# In[2]:


import requests
#import json  # for pretty-print with json.dump()
from time import time  # time() is added to GET requests to prevent any caching


# In[3]:


class ExpertSystem():
    
    # servlet_url
    
    def __init__(self,*,servlet_url):
        self.servlet_url = servlet_url
        
    def submitkbfn(self,*,datalog_filename,mode):
        with open(datalog_filename) as f:
            content = f.read()
            return self.submitkb(datalog_text=content,mode=mode)
    
    def submitkb(self,*,datalog_text,mode):
        if mode=='w': uc='learn'
        if mode=='a': uc='learnmore'
        rq = requests.post(self.servlet_url, json = {"uc":uc, "kb":datalog_text})
        print('reply:',rq.text, rq.ok, rq.status_code)
        assert rq.status_code==201
        return rq.json()
    
    def getkbstat(self):
        rq = requests.get(self.servlet_url, params = {'uc':'kb',"tm":time()})
        print('reply:',rq.ok, rq.status_code)
        assert rq.status_code==200
        return rq.json()
    
    def submitquery(self,query):
        rq = requests.get(self.servlet_url, params = {'uc':'query','qs':query,"tm":time()})
        print('reply:',rq.ok, rq.status_code)
        assert rq.status_code==200 or rq.status_code==204
        return rq.json()

# https://stackoverflow.com/questions/2965271/how-can-we-force-naming-of-parameters-when-calling-a-function


# ## I load the initial KNOWLEDGE BASE KB

# In[4]:


datalog_kb_folder = r'.'
datalog_filename = datalog_kb_folder + '\\mmind-datalog.ps'

es = ExpertSystem(servlet_url='http://localhost:8080/HelloWorldu')

es.submitkbfn(datalog_filename=datalog_filename,mode='w')
ansdict = es.getkbstat()
print('getkbstat:',ansdict)


# ## on the desk: I submit my guess n. 1; I get a feedback; I update the KB with both;

# In[5]:


more_knowledge = '''
isa_guess(g0,c0,c0,c0,c1).
isa_fback(g0,b,x,x,x).
%follows(gy,gx,gg).
'''
es.submitkb(datalog_text=more_knowledge,mode='a')
ansdict = es.getkbstat()
print('getkbstat:',ansdict)


# In[6]:


query = "minandmaxg(MINGN,MAXGN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[7]:


assert alen==1


# In[8]:


query = "isa_feedbackpermut(FBTRY, H0, H1, H2, H3)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[9]:


query = "isa_solution_exante(CH0,CH1,CH2,CH3)?" # 1296
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
assert alen == 6**4 # == 1296
devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## I get advice from the Engine (500 options out of 1296), based on the latest updates

# In[10]:


query = "isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[11]:


#delete:
if False:
    query = "isa_betterguess_post_g0(CH0,CH1,CH2,CH3)?"
    ans = es.submitquery(query)
    alen = len(ans['ans'])
    print('len(ans):',alen)
    devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## on the desk: I submit my guess n.2; I get a feedback; I update the KB;

# In[12]:


more_knowledge = '''
isa_guess(g1, c0, c5, c5, c5).
isa_fback(g1,x,x,x,x).
follows(g1,g0,gg).
'''
es.submitkb(datalog_text=more_knowledge,mode='a')
ansdict = es.getkbstat()
print('getkbstat:',ansdict)


# In[13]:


query = "minandmaxg(MINGN,MAXGN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[14]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[15]:


assert alen==2


# ## I get advice from the Engine (240 options), based on the latest updates

# In[16]:


#query = "isa_betterguess_post_g1(CH0,CH1,CH2,CH3)?"
query = "isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## on the desk: I submit my guess n.3; I get a feedback; I update the KB;

# In[17]:


more_knowledge = '''
isa_guess(g2, c5, c4, c2, c1).
isa_fback(g2,b,x,x,x).
follows(g2,g1,gg).
'''
es.submitkb(datalog_text=more_knowledge,mode='a')
ansdict = es.getkbstat()
print('getkbstat:',ansdict)


# In[18]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[19]:


assert alen==3


# In[20]:


query = "minandmaxg(MINGN,MAXGN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## I get advice from the Engine (92 options), based on the latest updates

# In[21]:


#query = "isa_betterguess_post_g2(CH0,CH1,CH2,CH3)?"
query = "isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## on the desk: I submit my guess n.4; I get a feedback; I update the KB;

# In[23]:


more_knowledge = '''
isa_guess(g3, c3, c0, c2, c0).
isa_fback(g3,b,b,b,x).
follows(g3,g2,gg).
'''
es.submitkb(datalog_text=more_knowledge,mode='a')
ansdict = es.getkbstat()
print('getkbstat:',ansdict)


# In[24]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[25]:


assert alen==4


# ## I get advice from the Engine (6 options), based on the latest updates

# In[26]:


query = "isa_betterguess_post_g3(CH0,CH1,CH2,CH3)?"
query = "isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## on the desk: I submit my guess n.5; I get a feedback; I update the KB;

# In[27]:


more_knowledge = '''
isa_guess(g4, c3, c0, c2, c3).
isa_fback(g4,b,b,b,x).
follows(g4,g3,gg).
'''
es.submitkb(datalog_text=more_knowledge,mode='a')
ansdict = es.getkbstat()
print('getkbstat:',ansdict)


# In[28]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[29]:


assert alen==5


# ## I get advice from the Engine (4 options), based on the latest updates

# In[30]:


query = "isa_betterguess_post_g4(CH0,CH1,CH2,CH3)?"
query = "isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## on the desk: I submit my guess n.6; I get a feedback; I update the KB;

# In[31]:


more_knowledge = '''
isa_guess(g5, c3, c0, c2, c4).
isa_fback(g5,b,b,b,b).
follows(g5,g4,gg).
'''
es.submitkb(datalog_text=more_knowledge,mode='a')
ansdict = es.getkbstat()
print('getkbstat:',ansdict)


# In[32]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[33]:


assert alen==6


# ## I get advice from the Engine (1 option), based on the latest updates

# In[34]:


query = "isa_betterguess_post_g5(CH0,CH1,CH2,CH3)?"
query = "isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[38]:


success = alen==1
print('success:',success)


# ## END - success: secret was (c3, c0, c2, c4)

# In[ ]:




