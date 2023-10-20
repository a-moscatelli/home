#!/usr/bin/env python
# coding: utf-8

# In[1]:


# alternatives to this python client:
# - the online service: https://datalog.db.in.tum.de/
# - the desktop GUI. Just run: java -jar AbcDatalog-0.6.0.jar


# In[2]:


import requests
from time import time  # time() is added to GET requests to prevent any caching
#import json  # only required for pretty-print with json.dump()


# In[3]:


datalog_kb_folder = r'M:\DEV\github__a_moscatelli\repositories\home\am-wiki-assets\logicprogramming\datalog-kb'
datalog_filename = datalog_kb_folder + '\\mmind-datalog.ps'

servlet_url='http://localhost:8080/HelloWorldu'


# In[4]:


class ExpertSystem():
    
    # generic datalog servlet client
    
    servlet_url = None
    
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
        print('reply: success=',rq.ok, 'status_code=',rq.status_code,'text:',rq.text)
        assert rq.status_code==201
        return rq.json()
    
    def getkbstat(self):
        rq = requests.get(self.servlet_url, params = {'uc':'kb',"tm":time()})
        print('reply: success=',rq.ok, 'status_code=',rq.status_code)
        assert rq.status_code==200 or rq.status_code==204 
        return rq.json()
    
    def submitquery(self,query):
        rq = requests.get(self.servlet_url, params = {'uc':'query','qs':query,"tm":time()})
        print('reply: success=',rq.ok, 'status_code=',rq.status_code)
        assert rq.status_code==200 or rq.status_code==204
        return rq.json()

# https://stackoverflow.com/questions/2965271/how-can-we-force-naming-of-parameters-when-calling-a-function


# In[5]:


class ExpertSystemMasterMind(ExpertSystem):
    guess=0
    funnel=[]
    
    def learnmore_GuessAndFeedback(self,*,gg,fb):
        skip_follows = '%' if self.guess==0 else ''
        more_knowledge_template = "api_isa_guess(g{0},{1}). api_isa_fback(g{0},{2}). {3} follows(g{0},g{4},gg)."
        more_knowledge = more_knowledge_template.format(self.guess,gg,fb,skip_follows,self.guess-1)
        # example: "isa_guess(g1,c0, c5, c5, c5). isa_fback(g1,x,x,x,x).  follows(g1,g0,gg)."
        print('adding:',more_knowledge)
        self.submitkb(datalog_text=more_knowledge,mode='a')
        ansdict = self.getkbstat()
        print('getkbstat:',ansdict)
        self.guess += 1
    
    def get_new_advice(self):
        query = "api_isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
        ans = self.submitquery(query)
        alen = len(ans['ans'])
        self.funnel.append(alen)
        print('len(ans):',alen)
        print('first ten:')
        devnull = [ print(a) for a in ans['ans'][0:10] ]
        return alen

    def print_submitted_guessnfeedbacks(self):
        query = "api_isa_validguessnfeedback(GN,GC0,GC1,GC2,GC3,FC0,FC1,FC2,FC3)?"
        ans = self.submitquery(query)
        alen = len(ans['ans'])
        print('len(ans):',alen)
        devnull = [ print(a) for a in sorted(ans['ans'][0:10]) ]
        return alen

    def print_initial_possible_solutions(self):
        query = "api_isa_solution_exante(CH0,CH1,CH2,CH3)?" # 1296
        ans = self.submitquery(query)
        alen = len(ans['ans'])
        print('len(ans):',alen)
        devnull = [ print(a) for a in sorted(ans['ans'][0:10]) ]
        return alen


# ### conventions

# In[6]:


# color codes: c0 c1 c2 c3 c4 c5 = red green blue yellow magenta cyan
# h0 h h2 h3 = the four holes
# b = black feedback peg, x = complementary meaning of black


# ## I load the initial KNOWLEDGE BASE KB

# In[7]:


es = ExpertSystemMasterMind(servlet_url=servlet_url)

es.submitkbfn(datalog_filename=datalog_filename,mode='w')
ansdict = es.getkbstat()
print('- getkbstat -') #,ansdict)
devnull = [ print(k,':',ansdict[k]) for k in ansdict.keys() ]


# ## possible solutions at start

# In[8]:


alen = es.print_initial_possible_solutions()
assert alen == 6**4


# In[9]:


es.funnel.append(alen)


# ## on the game app: I submit my guess n. 1 and I get a feedback. I update the KB:

# In[10]:


es.learnmore_GuessAndFeedback(gg='c0,c0,c0,c1',fb='b,x,x,x') # fb='b,o,o,o'


# In[11]:


alen=es.print_submitted_guessnfeedbacks()
assert alen==1


# ## I get advice from the Engine (500 options out of 1296), based on the latest updates

# In[12]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 2 and I get a feedback. I update the KB:

# In[13]:


es.learnmore_GuessAndFeedback(gg='c0, c5, c5, c5',fb='x,x,x,x') # fb='w,o,o,o'


# In[14]:


alen=es.print_submitted_guessnfeedbacks()
assert alen==2


# ## I get advice from the Engine (240 options), based on the latest updates

# In[15]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 3 and I get a feedback. I update the KB:

# In[16]:


es.learnmore_GuessAndFeedback(gg='c5, c4, c2, c1',fb='b,x,x,x') # fb='b,w,o,o'


# ## I get advice from the Engine (92 options), based on the latest updates

# In[17]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 4 and I get a feedback. I update the KB:

# In[18]:


es.learnmore_GuessAndFeedback(gg='c3, c0, c2, c0',fb='b,b,b,x') # fb='b,b,b,o'


# ## I get advice from the Engine (6 options), based on the latest updates

# In[19]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 5 and I get a feedback. I update the KB:

# In[20]:


es.learnmore_GuessAndFeedback(gg='c3, c0, c2, c3',fb='b,b,b,x') # fb='b,b,b,o'


# ## I get advice from the Engine (4 options), based on the latest updates

# In[21]:


es.get_new_advice()


# ## on the game app: I submit my guess n. 6 and I get a feedback. I update the KB:

# In[22]:


es.learnmore_GuessAndFeedback(gg='c3, c0, c2, c4',fb='b,b,b,b') # fb='b,b,b,b'


# ## I get advice from the Engine (1 option), based on the latest updates

# In[23]:


alen=es.get_new_advice()


# In[24]:


success = alen == 1
print('success:',success)


# ## END - success: secret was (c3, c0, c2, c4)

# In[25]:


es.funnel


# In[26]:


print(es.funnel == [1296, 500, 240, 92, 6, 2, 1])


# In[27]:


alen=es.print_submitted_guessnfeedbacks()


# In[28]:


assert alen==6 and success


# In[ ]:




