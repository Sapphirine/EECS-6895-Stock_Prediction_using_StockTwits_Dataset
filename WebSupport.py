import datetime
from StockTwitsDataset import STDataset
from StockTwits_TimeDomainAnalysis import QueryTimeDomainData
from StockTwits_AnalysisCorrelation import AnalysisCorrelation
import StockTwits_StockList as STSL
import copy
import pickle
from sklearn.naive_bayes import GaussianNB
import numpy as np

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

	def find_messages(self, stock, sentiment=None, query_date=None):
		# cur_hour =  datetime.datetime.now()
		# date = (cur_hour.year, cur_hour.month, cur_hour.day)
		# start = datetime.datetime(date[0], int(date[1]), date[2], 0, 0, 0)
		# cur_time = datetime.datetime(date[0], int(date[1]), date[2], cur_hour.hour)

		if query_date is None:
			cur_date =  datetime.datetime.today()
			# print(cur_date.hour)
			start = datetime.datetime(cur_date.year,cur_date.month,cur_date.day, 0, 0, 0)
			cur_time = datetime.datetime(start.year, start.month, start.day, cur_date.hour)
			if cur_date.hour < 19:
				start = start + datetime.timedelta(days=-1)
				cur_time = datetime.datetime(start.year, start.month, start.day, 23)
			print(start)
			print(cur_time)
			
			
		# print(sentiment)
		# print(stock)
		if sentiment is None:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}})
			# print(stock_message.count())
			#if type(stock_message) == "NoneType":
			if stock_message.count() == 0:
				stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}})
		elif sentiment >= 0:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}, 'entities':{'sentiment': {'basic': 'Bullish'}}})
			# print(type(stock_message))
			print("finding bearish message: ")
			print(stock_message.count())
			#if type(stock_message) == "NoneType":
			if stock_message.count() == 0:
				stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}})
		else:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}, 'entities':{'sentiment': {'basic': 'Bearish'}}})
			# print(type(stock_message))
			print(stock_message.count())
			#if type(stock_message) == "NoneType":
			if stock_message.count() == 0:
				stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}})

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

	def get_top_lists(self,query_date=None, topN=10):
		"""based on the query date, get top lists"""
		if query_date is None:
			cur_date =  datetime.datetime.today()
			# print(cur_date.hour)
			if cur_date.hour < 19:
				end_date = datetime.date(cur_date.year,cur_date.month,cur_date.day)
				cur_date = end_date + datetime.timedelta(days=-1)
			# print(cur_date)
			if len(str(cur_date)) > 11: 
				query_date = str(cur_date)[0:-16]
			else:
				query_date = str(cur_date)
		print(query_date)
		database = STDataset(database="bigdata")
		stocks = database.findDailyRank({"date":query_date})
		# print stocks
		stock_dict = stocks["popular"]
		stock_sentiment_dict = stocks["sentiment"]
		sorted_stock_dict = sorted(stock_dict.items(), key=lambda i: i[1], reverse=True)
		sorted_stock_sentiment_dict = sorted(stock_sentiment_dict.items(), key=lambda i: i[1], reverse=True)

		# topN = 8
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
		print(re)
		return re

	def get_time_query(self,query_date=None, span=6):
		if query_date is None:
			cur_date =  datetime.datetime.today()
			# print(cur_date.hour)
			if cur_date.hour < 19:
				end_date = datetime.date(cur_date.year,cur_date.month,cur_date.day)
				start_date = end_date + datetime.timedelta(days=-span)
			else:
				end_date = datetime.date(cur_date.year,cur_date.month,cur_date.day)
				yesterday = end_date + datetime.timedelta(days=-1)
				end_date = yesterday
				start_date = end_date + datetime.timedelta(days=-span)
			
			# print(start_date, end_date)
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
		# print(data)
		predict = anas.analysisStock(data_copied, stock_name)
		# print(predict)
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

	def get_prediction(self, stock_list, query_date=None):
		"""base on the stock, get machine learning features, trained model, and then make prediction"""
		if query_date is None:
			cur_date =  datetime.datetime.today()
			# print(cur_date.hour)
			if cur_date.hour < 19:
				end_date = datetime.date(cur_date.year,cur_date.month,cur_date.day)
				cur_date = end_date + datetime.timedelta(days=-1)
			# print(cur_date)
			if len(str(cur_date)) > 11: 
				query_date = str(cur_date)[0:-16]
			else:
				query_date = str(cur_date)
		# print(query_date)
		database = STDataset(database="bigdata")
		stocks = database.findDailyRank({"date":query_date})
		# print(stocks)
		stock_feature_dict = stocks["feature"]
		stock_prediction_dict = dict()
		for stock_name in stock_list:
			feature_list = stock_feature_dict[stock_name]
			# print(feature_list)
			# try:
			# 	model_file = "./ml_model/" + stock_name + ".ml"
			# 	scaler = pickle.load(open(model_file, 'rb'))
			# 	predict_result = scaler.predict_proba(feature_list)

			# 	print("loaded trained machine leanring model")
			# except:
			# 	print("error during loading trained machine learning model")

			model_file = "./ml_model/" + stock_name + ".ml"
			scaler = pickle.load(open(model_file, 'rb'))
			feature = np.matrix(feature_list).reshape(1, -1)
			# print(feature.shape)
			
			predict = scaler.predict(feature)
			predict_result = scaler.predict_proba(feature)[0]
			# print(predict)
			# print(predict_result)
			print("loaded trained machine leanring model")
			if predict_result[0] > predict_result[1]:
				# return 'Bearish', predict_result[0]*100
				# print(predict_result)
				predict_result = str("%.2f"%(predict_result[0]*100))
				stock_prediction_dict[stock_name] = ['Bearish', predict_result]
			else:
				# return 'Bullish', predict_result[1]*100
				predict_result = str("%.2f"% (predict_result[1]*100))

				stock_prediction_dict[stock_name] = ['Bullish', predict_result]
		# print(stock_prediction_dict)
		return stock_prediction_dict


if __name__ == '__main__':
	webSupport = TempClass()
	# webSupport.get_time_query()
	webSupport.get_top_lists()
	# webSupport.get_prediction(["AAPL"])
	# webSupport.find_messages("AMZN")
