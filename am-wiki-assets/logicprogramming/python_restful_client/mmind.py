import requests
from time import time  # time() is added to GET requests to prevent any caching

class ExpertSystemREST():
	
	# generic datalog servlet client
	
	servlet_url = None
	
	def __init__(self,*,servlet_url):
		self.servlet_url = servlet_url
		
	def submitkbfn(self,*,datalog_filename,mode='w'):
		with open(datalog_filename) as f:
			content = f.read()
			return self.submitkb(datalog_text=content,mode=mode)
	
	def submitkb(self,*,datalog_text,mode):
		assert mode in ['w','a']
		if mode=='w': uc='learn'
		if mode=='a': uc='learnmore'
		
		if mode=='w':
			rq = requests.delete(self.servlet_url)
			print('delete reply: success=',rq.ok, 'status_code=',rq.status_code, 'text:', rq.text)

		#rq = requests.post(self.servlet_url, json = {"uc":uc, "kb":datalog_text})
		rq = requests.post(self.servlet_url, json = {"kb":datalog_text})
		print('post reply: success=',rq.ok, 'status_code=',rq.status_code,'text:',rq.text)
		assert rq.status_code==201
		return rq.json()
	
	def getkbstat(self):
		rq = requests.get(self.servlet_url) # , params = {'uc':'kb',"tm":time()})
		print('getkbstat get reply: success=',rq.ok, 'status_code=',rq.status_code,'text:', rq.text)
		assert rq.status_code==200 or rq.status_code==204 
		return rq.json()
	
	def submitquery(self,query):
		#rq = requests.get(self.servlet_url, params = {'uc':'query','qs':query,"tm":time()})
		rq = requests.get(self.servlet_url, params = {'rule':query,"tm":time()})
		print('submitquery get reply: success=',rq.ok, 'status_code=',rq.status_code,'elapsed_ms:', rq.json()['elapsed_ms'])
		if False: print('rq.text',rq.text)
		assert rq.status_code==200 or rq.status_code==204
		if rq.status_code==204: return {'ans':[]}
		return rq.json()

	def submitquery_print_getlen(self, query, topn=10):
		return self.submitquery_and_print_r(query,topn)[0]
	
	def submitquery_print_getlist(self, query, topn=10):
		return self.submitquery_and_print_r(query,topn)[1]

	def submitquery_and_print_r(self, query, topn=10):
		assert topn > 0
		print('submitting query:',query)
		ans = self.submitquery(query)
		alen = len(ans['ans'])
		print('len(ans):',alen)
		if alen > 0 :
			print('ans.head',topn,':')
			print('===')
			devnull = [ print(a) for a in sorted(ans['ans'])[0:topn] ]	# you first sort then you take the topn
			print('===')
		return (alen,ans['ans'])
	
# https://stackoverflow.com/questions/2965271/how-can-we-force-naming-of-parameters-when-calling-a-function



class ExpertSystemMasterMind(ExpertSystemREST):
	guess=0
	funnel=[6**4] # solutions at start
	
	def learnmore_GuessAndFeedback(self,*,gg,fb):
		skip_follows = '%' if self.guess==0 else ''
		#more_knowledge_template = "api_isa_guess(g{0},{1}). api_isa_fback(g{0},{2}). {3} follows(g{0},g{4},gg)."
		more_knowledge_template = "api_isa_guess(g{0},{1}). api_isa_fback(g{0},{2}). {3} follows(g{0},g{4},gg)."
		more_knowledge = more_knowledge_template.format(self.guess,gg,fb,skip_follows,self.guess-1)
		# example: "isa_guess(g1,c0, c5, c5, c5). isa_fback(g1,x,x,x,x).  follows(g1,g0,gg)."
		print('adding:',more_knowledge)
		self.submitkb(datalog_text=more_knowledge,mode='a')
		ansdict = self.getkbstat()
		print('getkbstat(LMGS):',ansdict)
		self.guess += 1
	
	def get_new_advice(self, topn=10):
		#query = "api_isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
		query = "api_isa_validguess_evenafter_all_gg(CH0,CH1,CH2,CH3)?"
		ans = self.submitquery_print_getlist(query,topn)
		self.funnel.append(len(ans))
		return ans

	def print_submitted_guessnfeedbacks(self):
		query = "api_isa_validguessnfeedback(GID,GC0,GC1,GC2,GC3,FC0,FC1,FC2,FC3)?"
		alen = self.submitquery_print_getlen(query,100)
		return alen

	def print_initial_possible_solutions(self):
		query = "api_isa_solution_exante(CH0,CH1,CH2,CH3)?" # 1296
		alen = self.submitquery_print_getlen(query,10)
		return alen



class ExpertSystemMasterMindAssistant(ExpertSystemMasterMind):

	def util_csv2a(self,csv):
		return csv.replace(" ","").split(',')		

	def util_get_kurtosis(self,guess):
		if type(guess)==str:
			guess = self.util_csv2a(guess)
		assert type(guess)==list
		guess0counts = { i : guess.count(i) for i in guess} # {'c2': 1, 'c3': 2, 'c4': 1}
		kurt = sorted(guess0counts.values(),reverse=True) # you will have: 3-1
		kurts = '-'.join([str(k) for k in kurt])
		return kurts
	
	def util_get_kurtosis_n(self,guess):
		kurts = self.util_get_kurtosis(guess)
		ascend = ["1-1-1-1", "2-1-1", "2-2", "3-1", "4"]
		kurtn = ascend.index(kurts)
		return kurtn

	def util_get_array_from_answer(self,ans,returnarray):
		ax=ans.index('(')+1
		zx=ans.index(')')
		scut = ans[ax:zx]
		scuta = self.util_csv2a(scut)
		if returnarray: return scuta
		return scut

	def util_take_an_option(self,ans,mode):
		# needs: util_get_array_from_answer util_get_kurtosis_n util_get_kurtosis util_csv2a
		if mode == 'first':
			pick = 0
			scut = self.util_get_array_from_answer(ans[pick],False)
			return scut
		if mode == 'platyk':
			keys = [ self.util_get_array_from_answer(aa,False) for aa in ans ]
			keyvals = [ (self.util_get_kurtosis_n(k), k ) for k in keys ]
			sorted_tuples = sorted(keyvals,reverse=False)
			print('mode',mode,'taking',sorted_tuples[0])
			# The sorted() method sorts tuples by default, using the first item in each tuple. reverse=False = default = ascend
			return sorted_tuples[0][1]
		if mode == 'leptok':
			keys = [ self.util_get_array_from_answer(aa,False) for aa in ans ]
			keyvals = [ (self.util_get_kurtosis_n(k), k ) for k in keys ]
			sorted_tuples = sorted(keyvals,reverse=True)
			print('mode',mode,'taking',sorted_tuples[0])
			# The sorted() method sorts tuples by default, using the first item in each tuple. reverse=False = default = ascend
			return sorted_tuples[0][1]
		if mode == 'mesok':
			keys = [ self.util_get_array_from_answer(aa,False) for aa in ans ]
			keyvals = [ (self.util_get_kurtosis_n(k), k ) for k in keys ]
			sorted_tuples = sorted(keyvals,reverse=False)
			mi = int(len(sorted_tuples)/2) # the index of the middle of the list, ceil.
			print('mode',mode,'taking',sorted_tuples[mi])
			# int(len(list)/2) # tests: []=>0, [3]=>0, [3,3]=>1, [3,3,3]=>1, [3,3,3,3]=>2
			return sorted_tuples[mi][1]
		assert False, 'unkown mode'
		

class ExpertSystemMasterMindUser(ExpertSystemMasterMindAssistant):

	def util_get_feedback(self,*,secret,guess):
		#blank=chr(32) # " "
		sz=4
		secreta = self.util_csv2a(secret)
		guessa = self.util_csv2a(guess)
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
	
	


	def one_game_loop(self,*,datalog_filename,first_guess,secret,subseqpickmode): # loop: cracking the secret
		self.guess=0
		self.funnel=[]
		first_guesss = ','.join(first_guess)
		nextguess = first_guesss
		kurts = self.util_get_kurtosis(first_guess)
		secrets = ','.join(secret)
		# I load the initial KNOWLEDGE BASE KB
		self.submitkbfn(datalog_filename=datalog_filename,mode='w')
		ansdict = self.getkbstat()
		print('- getkbstat -') #,ansdict)
		devnull = [ print(k,':',ansdict[k]) for k in ansdict.keys() ]
		initial_possible_solutions = self.print_initial_possible_solutions()
		self.funnel=[initial_possible_solutions]
		assert initial_possible_solutions == 6**4
		options = initial_possible_solutions
		
		while options >1:
			print('nextguess:',nextguess)
			fb0 = self.util_get_feedback(secret=secrets,guess=nextguess)
			fb0s = ','.join(fb0)
			self.learnmore_GuessAndFeedback(gg=nextguess,fb=fb0s)
			alenfb = self.print_submitted_guessnfeedbacks()
			print('print_submitted_guessnfeedbacks:',alenfb)
			ans = self.get_new_advice()
			options = len(ans)
			assert options > 0, 'no options! the model is likely incorrect!'
			if options>0: nextguess = self.util_take_an_option(ans,subseqpickmode)
		
		SUCCESS = ", ".join(secret) == nextguess
		retdict = { # all strings
			"final_guess" : nextguess, # str
			"first_guess" : first_guesss, # str 
			"first_guess_kurts" : "K"+kurts,
			"guesses" : str(alenfb),
			"funnel" : 'F'+('-'.join([str(n) for n in self.funnel])), # self.funnel
			"subseqpickmode" : subseqpickmode,
			"secret" : secrets,
			"SUCCESS" : str(SUCCESS)
		}
		ret4tsv = '\t'.join(key +"\t"+ value for key, value in retdict.items())
		#return ret
		return ret4tsv