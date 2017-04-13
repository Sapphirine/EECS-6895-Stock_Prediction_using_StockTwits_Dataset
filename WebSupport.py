import datetime
from StockTwitsDataset import STDataset
from StockTwits_TimeDomainAnalysis import QueryTimeDomainData
from StockTwits_AnalysisCorrelation import AnalysisCorrelation
import StockTwits_StockList as STSL
import copy


class TempClass:

	def findMessages(self,query=None):
		try:
			database = STDataset("bigdata")
			db_client = database.db_client
			db = db_client["bigdata"]
			message_collection = db.messages
			outs = message_collection.find(query)
			return outs
		except Exception,e:
			"Error during find messages ..."
			print Exception,e
			return None

	def find_messages(self, stock, sentiment=None):
		cur_hour =  datetime.datetime.now()
		date = (cur_hour.year, cur_hour.month, cur_hour.day)
		start = datetime.datetime(date[0], int(date[1]), date[2], 0, 0, 0)
		cur_time = datetime.datetime(date[0], int(date[1]), date[2], cur_hour.hour)
		# print(sentiment)
		# print(stock)
		if sentiment is None:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}})
			# print(stock_message.count())
			#if type(stock_message) == "NoneType":
			if stock_message.count() == 0:
				stock_message = self.findMessages({'symbols': {'$elemMatch':{'symbol':stock}}})
		elif sentiment >= 0:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}, 'entities':{'sentiment': {'basic': 'Bullish'}}})
			# print(type(stock_message))
			# print(stock_message.count())
			#if type(stock_message) == "NoneType":
			if stock_message.count() == 0:
				stock_message = self.findMessages({'symbols': {'$elemMatch':{'symbol':stock}}})
		else:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}, 'entities':{'sentiment': {'basic': 'Bearish'}}})
			# print(type(stock_message))
			# print(stock_message.count())
			#if type(stock_message) == "NoneType":
			if stock_message.count() == 0:
				stock_message = self.findMessages({'symbols': {'$elemMatch':{'symbol':stock}}})

		message = []
		try:
			for m in stock_message[0:10]:
				cur_m = dict()
				# pprint.pprint(m)
				m = dict(m)
				cur_m['body'] = m['body']
				cur_m['username'] = m['user']['username']
				cur_m['time'] = m['created_at']
				message.append(cur_m)
		except:
			pass
		return message

	def get_messages(self,stock, sentiment=None):
		#analyzer = StockTwits_Analysis.STAnalysis(database="bigdata")
		messages = self.find_messages(stock, sentiment=sentiment)
		#print(messages)
		return messages

	def get_top_lists(self,query_date=None):
		"""based on the query date, get top lists"""
		if query_date is None:
			cur_hour =  datetime.datetime.now()
			query_date = str(cur_hour)[0:-16]
			#print("date: " + query_date)
		database = STDataset(database="bigdata")
		stocks = database.findDailyRank({"date":query_date})
		#print stocks
		stock_dict = stocks["popular"]
		stock_sentiment_dict = stocks["sentiment"]
		sorted_stock_dict = sorted(stock_dict.items(), key=lambda i: i[1], reverse=True)
		sorted_stock_sentiment_dict = sorted(stock_sentiment_dict.items(), key=lambda i: i[1], reverse=True)

		topN = 8
		re = {"popular":[],"bearish":[],"bullish":[]}
		for i in range(topN):
			stock = sorted_stock_dict[i]
			re["popular"].append({"name":stock[0],"score":str("%.2f"%stock[1])})

		for i in range(topN):
			stock = sorted_stock_sentiment_dict[i]
			re["bullish"].append({"name":stock[0],"score":str("%.2f"%stock[1])})

		for i in range(len(sorted_stock_sentiment_dict)-1, len(sorted_stock_sentiment_dict)-topN-1, -1):
			stock = sorted_stock_sentiment_dict[i]
			re["bearish"].append({"name":stock[0],"score":str("%.2f"%stock[1])})
		#print(re)
		return re

	def get_time_query(self,query_date=None, span=6):
		if query_date is None:
			cur_date =  datetime.datetime.today()
			end_date = datetime.date(cur_date.year,cur_date.month,cur_date.day)
			start_date = end_date + datetime.timedelta(days=-span)
			#print(start_date, end_date)
		ana = QueryTimeDomainData("bigdata")
		data, time_string_list = ana.queryData(start_date,end_date, STSL.ALL_LIST)
		# print(data)
		return data, time_string_list

	def get_popular_time(self,data, time_string_list):
		popular = data['COP']['popular']
		popular_time = zip(time_string_list, popular)
		#print(popular_time)
		return_json = {"popular":[["Time","popular"]]}
		
		for i in range(len(popular)):
			return_json["popular"].append([str(time_string_list[i]), float(popular[i])])	
		# print(return_json)
		return return_json

	def get_predict(self,data, stock_name):
		anas = AnalysisCorrelation()
		data_copied = copy.deepcopy(data)
		print(data)
		predict = anas.analysisStock(data_copied, stock_name)
		print(predict)
		return predict

	def get_close_price(self,data, stock_name):
		#print("in close price")
		#print(data)
		close_list = []
		weekend_index = []
		for i in range(len(data[stock_name]['price'])):
			if  data[stock_name]['price'][i] is None:
				# close_list.append(0)
				weekend_index.append(i)
			else:
				close = data[stock_name]['price'][i]['Adj Close'] 
				close_list.append(float(str(close)))
		return close_list, weekend_index