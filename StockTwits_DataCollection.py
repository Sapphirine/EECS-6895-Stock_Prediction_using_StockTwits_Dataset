from __future__ import division
import requests, json
from StockTwitsDataset import STDataset 
from stockTwits_analysis import STAnalysis
import time

ENEGY = ['XOM','PXD','CVX','HAL','COP']
BASIC_MATERIALS = ['FCX','X','IP','LYB','VMC']
INDUSTRIALS = ['GE','BA','UNP','MMM','CAT']
CYCLICAL_CON_GOODS_SERVICES = ['DIS','TSLA','NFLX','ORLY','SBUX']
FINANCIALS = ['SPY','BAC','QQQ','JPM','C']
HEALTHCARE = ['GILD','BMY','PFE','JNJ','AMGN']
TECHNOLOGY = ['AAPL','AMZN','NVDA','CTSH','MSFT','AMD']
TELECOMMUNICATIONS = ['VZ','T','CMCSA','CTL']
UTILITIES = ['EXC','NEE','EIX','DUK','D']

ALL_LIST = ENEGY+BASIC_MATERIALS+INDUSTRIALS+CYCLICAL_CON_GOODS_SERVICES+FINANCIALS+HEALTHCARE+TECHNOLOGY
ALL_LIST += TELECOMMUNICATIONS + UTILITIES

def get_access_token():
	"""get access token"""
	url = "https://api.stocktwits.com/api/2/oauth/token"
	# data = {'client_id': '6b46df9ec2b8405d', 'client_secret': '2b88d5f2a05e9e62ec55fa83d9e784a78f8a27b0', 'code': 'fcbd9b06661f6134a007dadbdc87631f3de8b246', 'grant_type': 'authorization_code', 'redirect_uri': 'https://stocktwits.com'}
	data = "client_id=6b46df9ec2b8405d&client_secret=2b88d5f2a05e9e62ec55fa83d9e784a78f8a27b0&code=fcbd9b06661f6134a007dadbdc87631f3de8b246&grant_type=authorization_code&redirect_uri=https://stocktwits.com"
	r = requests.post(url, data=data)
	print(r)
	print(r.json())
	"""
	<Response [200]>
    {u'username': u'Raetweet', u'access_token': u'8b11310f68b976aac2acee575f3ed9e4a5d0de54', u'user_id': 936847,
     u'scope': u'read,watch_lists,direct_messages,publish_messages,publish_watch_lists,follow_users,follow_stocks'}
	"""
class StockTwits_DataObtain:
	def __init__(self):
		self.symbol_list = []
		self.user_list = []
		self.db = STDataset("user1","abcd1234","45.33.45.39","bigdata")
		self.request_count = 0
		self.request_start = int(time.time())
                self.access_token = '1e696733008f62184a4c97ea5912471b67123272'
		
	# stocks is a list	
	def requestStocksSteam(self,stocks):
		if self.request_count >= 400:
			return False
		st = ""
		s = 0
		messages = []
		symbols = []
		for vs in stocks:
			try:
				st += str(vs["id"])
			except:
				st += str(vs)
			s += 1
			if s == 10 or vs == stocks[-1]:
				url = "https://api.stocktwits.com/api/2/streams/symbols.json?symbols="+st+"&access_token="+self.access_token
				r = requests.get(url)
				self.request_count += 1
				data = r.json()
				messages = messages + data["messages"]
				#self.logJson(messages)
				st = ""
				s = 0
			else:
				st += ","
		
		news = self.db.saveMessages(messages)#add news to the list
		users = []
		for vs in news:
			try:
				users.append(vs["user"])
			except:
				pass
		
		for vs in messages:
			try:
				symbols += vs["symbols"]
			except:
				pass
		
		#self.logJson(symbols)
		#save new user information
		new_user = self.db.saveUsers(users)
		new_symbols = self.db.saveStockRecords(symbols)
		print "Get total "+str(len(messages))+" messages, "+str(len(news))+" are news, " +str(len(new_user))+" users updated " + str(len(new_symbols)) + " symbols updated"
		
		#add new user to the list
		#self.user_list = list(set(self.user_list).union(set([c["id"] for c in new_user])))
		
		return len(news)/len(messages)
	
	# user id
	def requestUserSteam(self,user_id):
		if self.request_count >= 400:
			return False
		url = "https://api.stocktwits.com/api/2/streams/user/"+user_id+".json?access_token="+self.access_token
		r = requests.get(url)
		messages = r.json()
		news = self.db.saveMessages(messages)
		
		symbol_list = []
		
		for each in news:
			for sy in each["symbols"]:
				symbol_list.append(sy)
				
		new_symbols = self.db.saveStockRecords(symbol_list)
		self.symbol_list = list(set(self.symbol_list).union(set([c["id"] for c in new_symbols])))
		
		#no users should be put into user queue
		return True
		
	# request new messages
	def requestNewMessages(self):
		if self.request_count >= 400:
			return False
		url = "https://api.stocktwits.com/api/2/streams/all.json?access_token="++self.access_token
		r = requests.get(url)
		self.request_count += 1
		data = r.json()
		messages = data["messages"]
		news = self.db.saveMessages(messages)
		user_list = []
		symbol_list = []
		for each in news:
			user_list.append(each["user"])
			symbol_list += each["symbols"]
		
		#self.logJson(symbol_list)
		
		new_users = self.db.saveUsers(user_list)
		new_symbols = self.db.saveStockRecords(symbol_list)
		print "Get total "+str(len(messages))+" messages, "+str(len(news))+" are news, " +str(len(new_users))+" users updated " + str(len(new_symbols)) + " symbols updated"
		
		#self.user_list = list(set(self.user_list).union(set([c["id"] for c in new_users])))
		#self.symbol_list = list(set(self.symbol_list).union(set([c["id"] for c in new_symbols])))
		return len(news)/len(messages)
	
	def logJson(self,news):
		output = open("log.txt","w+")
		st = json.dumps(news, sort_keys=True, indent=4, separators=(',', ': '))
		output.write('------- '+str(int(time.time()))+' -------\n')
		output.write(st)
		output.flush()
		output.close()
		
		
	def run(self):
		last_time_request_news = 0
		last_time_request_users = 0
		last_time_request_stocks = 0
		stocks_delay = 60
		news_delay = 60
                do_news = False
		while True:
			try:
				if int(time.time())-self.request_start >3600: #every hour
					self.request_count = 0
					"""analyze and update scores"""
					analyzer = STAnalysis(database="bigdata")
					analyzer.analysisPopularityEveryHour()
					print("Updating Scores ...")
					# break
				if (int(time.time()) - last_time_request_news > news_delay and do_news):
					last_time_request_news = int(time.time())
					print("Request News ... ")
					ratio = self.requestNewMessages()
					if ratio < 0.1:
						news_delay = 180
					elif ratio < 0.5:
						news_delay = 120
					elif ratio < 0.8:
						news_delay = 60
					else:
						news_delay = 20
					if ratio<0.9:
						last_time_request_stocks = int(time.time()) #no need to request stocks
				if (int(time.time()) - last_time_request_stocks > stocks_delay):
					last_time_request_stocks = int(time.time())
					print("Request Stocks ... ")
					ratio = self.requestStocksSteam(ALL_LIST)
					if ratio < 0.2:
						stocks_delay = 180
					elif ratio < 0.5:
						stocks_delay = 120
					else:
						stocks_delay = 60
					
				time.sleep(1)
			except Exception,e:
				print Exception,e

if __name__ == "__main__":
	print("start data collection")
	obtain = StockTwits_DataObtain()
	obtain.run()
	#news = obtain.requestStocksSteam(["SXE"])
	#output = open("AMD.txt","w")
	
	#st = json.dumps(news, sort_keys=True, indent=4, separators=(',', ': '))
	#output.write(st)
	#output.flush()
	#output.close()
	#print len(db.saveMessages(messages))
	#st = json.dumps(messages)
	#print(json.dumps(messages, sort_keys=True, indent=4, separators=(',', ': ')))
