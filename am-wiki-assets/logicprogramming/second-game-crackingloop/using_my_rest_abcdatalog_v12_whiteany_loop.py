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
        if False: print('rq.text',rq.text)
        assert rq.status_code==200 or rq.status_code==204
        if rq.status_code==204: return {'ans':[]}
        return rq.json()

    def submitquery_and_print(self,query,topn=10,fullans=False):
        assert topn > 0
        print('submitting query:',query)
        ans = self.submitquery(query)
        alen = len(ans['ans'])
        print('len(ans):',alen)
        if alen > 0 :
            print('ans.head',topn,':')
            print('===')
            devnull = [ print(a) for a in sorted(ans['ans'][0:topn]) ]
            print('===')
        if fullans: return ans['ans']
        return alen
    
# https://stackoverflow.com/questions/2965271/how-can-we-force-naming-of-parameters-when-calling-a-function


# In[5]:


class ExpertSystemMasterMind(ExpertSystem):
    guess=0
    funnel=[]
    
    def learnmore_GuessAndFeedback(self,*,gg,fb):
        
        #fb=fb.replace('o','x').replace('w','x')
        
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
        ans = self.submitquery_and_print(query,10,fullans=True)
        alen = len(ans)
        self.funnel.append(alen)
        return ans

    def print_submitted_guessnfeedbacks(self):
        query = "api_isa_validguessnfeedback(GN,GC0,GC1,GC2,GC3,FC0,FC1,FC2,FC3)?"
        alen = self.submitquery_and_print(query,100)
        return alen

    def print_initial_possible_solutions(self):
        query = "api_isa_solution_exante(CH0,CH1,CH2,CH3)?" # 1296
        alen = self.submitquery_and_print(query,10)
        return alen

    def util_get_feedback(self,*,secret,guess):
        blank=chr(32) # " "
        sz=4
        secreta = secret.replace(blank,"").split(',')
        guessa = guess.replace(blank,"").split(',')
        assert len(secreta)==sz and len(guessa)==sz
        bb=0
        ww=0
        for hh in range(0,4): # black loop
            if guessa[hh] == secreta[hh]:
                bb+=1
                secreta[hh]='@b'
                guessa[hh]='#b'
        for hh in range(0,4): # white loop
            if guessa[hh] != '#b' and guessa[hh] in secreta:
                hw = secreta.index(guessa[hh])
                ww+=1
                secreta[hw]='@w'

        return ['b'] * bb + ['w'] * ww + ['o'] * (sz-bb-ww)
    def utile_take_first_guess(self,ans):
        ax=ans[0].index('(')+1
        zx=ans[0].index(')')
        return ans[0][ax:zx]


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


# ### generating the secret and the first guess - both randomly

# In[8]:


import random


# In[9]:


if False: random.seed(23)
secret = [ 'c'+str(random.randint(0, 5)) for i in range(0,4)] # randint() convention: both included
secrets = ','.join(secret)


# In[10]:


if True: random.seed(23)
guess0 = [ 'c'+str(random.randint(0, 5)) for i in range(0,4)] # randint() convention: both included
guess0 # blue red red magenta
nextguess = ','.join(guess0)


# ## possible solutions at start

# In[11]:


alen = es.print_initial_possible_solutions()
es.funnel.append(alen)
assert alen == 6**4


# ## loop: cracking the secret

# In[12]:


while alen >1:
    print('nextguess:',nextguess)
    fb0 = es.util_get_feedback(secret=secrets,guess=nextguess)
    fb0s = ','.join(fb0)
    es.learnmore_GuessAndFeedback(gg=nextguess,fb=fb0s)
    alenfb=es.print_submitted_guessnfeedbacks()
    print('print_submitted_guessnfeedbacks:',alenfb)
    ans=es.get_new_advice()
    alen=len(ans)
    nextguess = es.utile_take_first_guess(ans)


# ### summary

# In[22]:


print('secret=',secret)
print('last guess=',nextguess)
print('first guess=',guess0)
print('guesses=',alenfb)
assert ", ".join(secret) == nextguess


# In[23]:


print('es.funnel (evolution of scope of possible options)',es.funnel)


# In[15]:


alen=es.print_submitted_guessnfeedbacks()


# ### END

# In[ ]:




