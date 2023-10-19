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
    # generic datalog servlet client
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
        assert rq.status_code==200 or rq.status_code==204 
        return rq.json()
    
    def submitquery(self,query):
        rq = requests.get(self.servlet_url, params = {'uc':'query','qs':query,"tm":time()})
        print('reply:',rq.ok, rq.status_code)
        assert rq.status_code==200 or rq.status_code==204
        return rq.json()

# https://stackoverflow.com/questions/2965271/how-can-we-force-naming-of-parameters-when-calling-a-function


# In[4]:


class ExpertSystemMasterMind(ExpertSystem):
    guess=0
    funnel=[]
    
    def learnmore_GuessAndFeedback(self,*,gg,fb):
        skip_follows = '%' if self.guess==0 else ''
        more_knowledge = "isa_guess(g{0},{1}). isa_fback(g{0},{2}). {3} follows(g{0},g{4},gg).".format(
            self.guess,gg,fb,skip_follows,self.guess-1)
        print('adding:',more_knowledge)
        self.submitkb(datalog_text=more_knowledge,mode='a')
        ansdict = self.getkbstat()
        print('getkbstat:',ansdict)
        self.guess += 1
    
    def get_new_advice(self):
        query = "isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
        ans = self.submitquery(query)
        alen = len(ans['ans'])
        self.funnel.append(alen)
        print('len(ans):',alen)
        print('first ten:')
        devnull = [ print(a) for a in ans['ans'][0:10] ]


# ## I load the initial KNOWLEDGE BASE KB

# In[5]:


datalog_kb_folder = r'M:\DEV\github__a_moscatelli\repositories\home\am-wiki-assets\logicprogramming\datalog-kb'
datalog_filename = datalog_kb_folder + '\\mmind-datalog.ps'

es = ExpertSystemMasterMind(servlet_url='http://localhost:8080/HelloWorldu')

es.submitkbfn(datalog_filename=datalog_filename,mode='w')
ansdict = es.getkbstat()
print('- getkbstat -') #,ansdict)
devnull = [ print(k,':',ansdict[k]) for k in ansdict.keys() ]


# ## on the game app: I submit my guess n. 1
# ## I get a feedback.
# ## I update the KB:

# In[6]:


es.learnmore_GuessAndFeedback(gg='c0,c0,c0,c1',fb='b,x,x,x')


# ### just testing

# In[7]:


query = "minandmaxg(MINGN,MAXGN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[8]:


assert alen==1


# In[9]:


query = "isa_solution_exante(CH0,CH1,CH2,CH3)?" # 1296
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
assert alen == 6**4 # == 1296
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[10]:


es.funnel.append(alen)


# ## I get advice from the Engine (500 options out of 1296), based on the latest updates

# In[11]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 2
# ## I get a feedback.
# ## I update the KB:

# In[12]:


es.learnmore_GuessAndFeedback(gg='c0, c5, c5, c5',fb='x,x,x,x')


# ### just testing

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


es.get_new_advice()


# ## on the game app: I submit my guess n. 3
# ## I get a feedback.
# ## I update the KB:

# In[17]:


es.learnmore_GuessAndFeedback(gg='c5, c4, c2, c1',fb='b,x,x,x')


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


es.get_new_advice()


# ## on the game app: I submit my guess n. 4
# ## I get a feedback.
# ## I update the KB:

# In[22]:


es.learnmore_GuessAndFeedback(gg='c3, c0, c2, c0',fb='b,b,b,x')


# In[23]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[24]:


assert alen==4


# ## I get advice from the Engine (6 options), based on the latest updates

# In[25]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 5
# ## I get a feedback.
# ## I update the KB:

# In[26]:


es.learnmore_GuessAndFeedback(gg='c3, c0, c2, c3',fb='b,b,b,x')


# In[27]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[28]:


assert alen==5


# ## I get advice from the Engine (4 options), based on the latest updates

# In[29]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 6
# ## I get a feedback.
# ## I update the KB:

# In[30]:


es.learnmore_GuessAndFeedback(gg='c3, c0, c2, c4',fb='b,b,b,b')


# ### just testing

# In[31]:


query = "isa_validguesswithfb(GN)?"
ans = es.submitquery(query)
alen = len(ans['ans'])
print('len(ans):',alen)
devnull = [ print(a) for a in ans['ans'][0:10] ]


# In[32]:


assert alen==6


# ## I get advice from the Engine (1 option), based on the latest updates

# In[33]:


es.get_new_advice()


# In[34]:


success = alen==1
print('success:',success)


# ## END - success: secret was (c3, c0, c2, c4)

# In[35]:


es.funnel


# In[36]:


print(es.funnel == [1296, 500, 240, 92, 6, 2, 1])


# In[ ]:




