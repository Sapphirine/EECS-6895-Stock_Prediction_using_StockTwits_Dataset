'''
Created on Feb 12, 2017

@author: Tianrui Peng, Jia Ji
'''
import StockTwitsDataset
from pymongo import MongoClient
import pprint
import datetime
import math
import time
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from yahoo_finance import Share
import pandas as pd
import pandas_datareader.data as web
import StockTwits_StockList as STSL
#ENEGY = ['XOM','PXD','CVX','HAL','COP']
#BASIC_MATERIALS = ['FCX','X','IP','LYB','VMC']
#INDUSTRIALS = ['GE','BA','UNP','MMM','CAT']
#CYCLICAL_CON_GOODS_SERVICES = ['DIS','TSLA','NFLX','ORLY','SBUX']
#FINANCIALS = ['SPY','BAC','QQQ','JPM','C']
#HEALTHCARE = ['GILD','BMY','PFE','JNJ','AMGN']
#TECHNOLOGY = ['AAPL','AMZN','NVDA','CTSH','MSFT']
#TELECOMMUNICATIONS = ['VZ','T','CMCSA','CTL']
#UTILITIES = ['EXC','NEE','EIX','DUK','D']
#all_stocks = ['XOM', 'PXD', 'CVX', 'HAL', 'COP', 'FCX', 'X', 'IP', 'LYB', 'VMC', 'GE', 'BA', 'UNP', 'MMM', 'CAT', 'DIS', 'TSLA', 'NFLX', 'ORLY', 'SBUX', 'SPY', 'BAC', 'QQQ', 'JPM', 'C', 'GILD', 'BMY', 'PFE', 'JNJ', 'AMGN', 'AAPL', 'AMZN', 'NVDA', 'CTSH', 'MSFT', 'VZ', 'T', 'CMCSA', 'CTL', 'EXC', 'NEE', 'EIX', 'DUK', 'D']
all_stocks = STSL.ALL_LIST
class STAnalysis:
	def __init__(self,database,user=None,pwd=None,url=None):
		try:
			self.database = StockTwitsDataset.STDataset(database, user, pwd, url)
			self.db_client = self.database.db_client
			self.db = self.db_client[database]
			self.message_collection = self.db.messages
			self.user_collection = self.db.users
			self.stock_collection = self.db.stock
			self.stock_daily_collection = self.db.stock_daliy
			self.list_of_stocks = all_stocks
			print("the number of stocks: " + str(len(self.list_of_stocks)))
		except Exception,e:
			print e
			print "Error during connect to MongoDB init ... "

	def findMessages(self,query=None):
		try:
			outs = self.message_collection.find(query)
			return outs
		except Exception,e:
			"Error during find messages ..."
			print Exception,e
			return None

	def findStockRecords(self,query):
		try:
			outs = self.stock_collection.find(query)
			return outs
		except Exception,e:
			"Error during find stock ..."
			print Exception,e
			return None

	def findMessageOneDay(self, date):
		start = datetime.datetime(date[0], int(date[1]), date[2], 0, 0, 0)
		end = start + datetime.timedelta(days=1)
		# print("start date and end date")
		# print(start, end)
		outs = self.findMessages({'created_at': {'$gte': start.isoformat(), '$lt':end.isoformat()}})
		print("the number of message on date " + str(start) + " : " + str(outs.count()))
		return outs

	def findMessageOneHour(self,date, hour):
		start = datetime.datetime(date[0], int(date[1]), date[2], 0, 0, 0)
		cur_time = datetime.datetime(date[0], int(date[1]), date[2], hour)
		print("start date and current hour")
		print(start, cur_time)
		outs = self.findMessages({'created_at': {'$gte': start.isoformat(), '$lt':cur_time.isoformat()}})
		print("the number of message on date " + str(start) + ":" + str(outs.count()))
		# return outs

	def analysisPopularityOneDay(self, date, verbose=False):
		start = datetime.datetime(date[0], int(date[1]), date[2], 0, 0, 0)
		end = start + datetime.timedelta(days=1)
		yesterday = start + datetime.timedelta(days=-1)

		stock_dict = dict()
		stock_sentiment_dict = dict()

		yesterday_str = str(yesterday)[0:-9]
		print("yesterday: " + yesterday_str)
		query_result = self.database.findDailyRank({'date':yesterday_str})
		print(query_result)
		if query_result != None and "popular" in query_result and "sentiment" in query_result:
			yesterday_popularity = query_result["popular"]
			yesterday_sentiment = query_result["sentiment"]
		else:
			yesterday_popularity = 0
			yesterday_sentiment = 0

		for stock in self.list_of_stocks:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':end.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}})
			m_score, watchlist_count, trending_score, sentiment_score = self.caculateMessageScore(stock_message, stock)
			if verbose:
				print(stock)
				print("the number of message: " + str(stock_message.count()))
				print("m_score, watchlist_count, trending_score, sentiment_score")
				print(m_score, watchlist_count, trending_score, sentiment_score)

			if query_result != None: #if there is a yesterday popurality score
				if m_score == 0 or watchlist_count == 0: #if there is no message that day
					stock_dict[stock] = trending_score*10*0.75 + yesterday_popularity[stock]*0.25
				else:
					today_score  = (math.log(m_score, 2) + math.log(watchlist_count, 2) + trending_score*10)
					stock_dict[stock] = today_score*0.75 + yesterday_popularity[stock]*0.25
					if verbose:
						print("reading yesterday popularity score")
						print(today_score, yesterday_popularity[stock], stock_dict[stock])
					# print("log m score, log watchlist_count: " + str(math.log(m_score, 2))) + " " + str(math.log(watchlist_count, 2))
				stock_sentiment_dict[stock] = sentiment_score*0.75 + yesterday_sentiment[stock]*0.25
			else:
				if m_score == 0 or watchlist_count == 0: #if there is no message that day
					stock_dict[stock] = trending_score*10
				else:
					stock_dict[stock] = math.log(m_score, 2) + math.log(watchlist_count, 2) + trending_score*10
					# print("log m score, log watchlist_count: " + str(math.log(m_score, 2))) + " " + str(math.log(watchlist_count, 2))
				stock_sentiment_dict[stock] = sentiment_score
				
		# print(stock_dict)
		sorted_stock_dict = sorted(stock_dict.items(), key=lambda i: i[1], reverse=True)
		sorted_stock_sentiment_dict = sorted(stock_sentiment_dict.items(), key=lambda i: i[1], reverse=True)
		# print(sorted_stock_dict)
		# print(sorted_stock_sentiment_dict)
		if date[2] < 10:
			date_str = str(date[0]) + "-" + str(date[1]) + "-" + '0' + str(date[2])
			print(date_str)
		else:
			date_str = str(date[0]) + "-" + str(date[1]) + "-" + str(date[2])

		ranklist = {
			"popular": stock_dict,
			"sentiment": stock_sentiment_dict,
			# "date": time.strftime("%Y-%m-%d", time.localtime())
			"date": date_str
		}
		# print(ranklist)
		self.database.saveDailyRank(ranklist)
		# query_result = self.database.findDailyRank({"date": time.strftime("%Y-%m-%d", time.localtime())})
		return sorted_stock_dict, sorted_stock_sentiment_dict


	def analysisPopularityEveryHour(self, date=None, hour=None, verbose=False):
		no_input_date= False
		if date==None or hour == None:
			cur_hour =  datetime.datetime.now()
			date = (cur_hour.year, cur_hour.month, cur_hour.day)
			# print(date)
			hour = cur_hour.hour
			no_input_date = True
		# no_input_date = True
		start = datetime.datetime(date[0], int(date[1]), date[2], 0, 0, 0)
		cur_time = datetime.datetime(date[0], int(date[1]), date[2], hour)
		today_str = str(start)[0:-9]
		print("today_str: " + today_str)
		print("current time: " + str(cur_time))
		#stockdict{symbol: [message_score]}
		stock_dict = dict()
		stock_sentiment_dict = dict()
		stock_price_dict = dict()

		"""find yesterday scores"""
		yesterday = start + datetime.timedelta(days=-1)
		yesterday_str = str(yesterday)[0:-9]
		print("yesterday: " + yesterday_str)
		query_result = self.database.findDailyRank({'date':yesterday_str})
		print("query_result: " + str(query_result))
		if query_result != None and "popular" in query_result and "sentiment" in query_result:
			yesterday_popularity = query_result["popular"]
			yesterday_sentiment = query_result["sentiment"]
		else:
			query_result=None

		for stock in self.list_of_stocks:
			"""get opening price for all stocks"""
			# try:
			if no_input_date: #get today opening price
				stock_price = self.get_stock_price(stock)
				stock_price_dict[stock] = stock_price
			else: #api cannot get historical data for year 2016 and 2017
				end_date = start + datetime.timedelta(days=1)
				# print(today_str, end_date)
				try:
					stock_price = self.get_stock_price_update(stock, start, end_date).ix[today_str]
					stock_price_dict[stock] = dict(stock_price)
				except:
					print("Cannot get the price. Maybe the market is closed. (during weekends)")
					stock_price_dict[stock] = None
				# print(stock_price)
				# print(dict(stock_price))
			# except Exception as e:
			# 	print("Error when getting stock prices. (Might becuase there is no opening price yet) :" + str(e))

			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}})
			m_score, watchlist_count, trending_score, sentiment_score = self.caculateMessageScore(stock_message, stock, verbose=verbose)
			if query_result != None: #if there is a yesterday popurality score
				if m_score == 0 or watchlist_count == 0: #if there is no message that day
					stock_dict[stock] = trending_score*10*0.75 + yesterday_popularity[stock]*0.25
				else:
					stock_dict[stock] = (math.log(m_score, 2) + math.log(watchlist_count, 2) + trending_score*10)*0.75 + yesterday_popularity[stock]*0.25
					# print("log m score, log watchlist_count: " + str(math.log(m_score, 2))) + " " + str(math.log(watchlist_count, 2))
				# if yesterday_sentiment[stock] == 0 and sentiment_score == 0:
				# 	stock_sentiment_dict[stock] = 0
				# elif sentiment_score == 0:
				# 	stock_sentiment_dict[stock] = math.log(yesterday_sentiment[stock],2)*0.25
				# elif yesterday_sentiment[stock] == 0:
				# 	stock_sentiment_dict[stock] = math.log(sentiment_score, 2)		
				# else:
				# 	print(sentiment_score, yesterday_sentiment[stock])
				# 	stock_sentiment_dict[stock] = math.log(sentiment_score,2)*0.75 + math.log(yesterday_sentiment[stock],2)*0.25
				stock_sentiment_dict[stock] = sentiment_score*0.75 + yesterday_sentiment[stock]*0.25
			else:
				if m_score == 0 or watchlist_count == 0: #if there is no message that day
					stock_dict[stock] = trending_score*10
				else:
					stock_dict[stock] = math.log(m_score, 2) + math.log(watchlist_count, 2) + trending_score*10
					# print("log m score, log watchlist_count: " + str(math.log(m_score, 2))) + " " + str(math.log(watchlist_count, 2))

				# if sentiment_score == 0:
				# 	stock_sentiment_dict[stock] = sentiment_score
				# else:
				# 	stock_sentiment_dict[stock] = math.log(sentiment_score,2)
				stock_sentiment_dict[stock] = sentiment_score
			if verbose:
				print(stock)
				print("the number of message: " + str(stock_message.count()))
				print("m_score, watchlist_count, trending_score, sentiment_score")
				print(m_score, watchlist_count, trending_score, sentiment_score)

				
		# print(stock_dict)
		sorted_stock_dict = sorted(stock_dict.items(), key=lambda i: i[1], reverse=True)
		sorted_stock_sentiment_dict = sorted(stock_sentiment_dict.items(), key=lambda i: i[1], reverse=True)
		# print(sorted_stock_dict)
		# print(sorted_stock_sentiment_dict)

		ranklist = {
			"popular": stock_dict,
			"sentiment": stock_sentiment_dict,
			"price": stock_price_dict,
			# "date": time.strftime("%Y-%m-%d", time.localtime())
			"date": today_str
		}
		print(ranklist)
		self.database.saveDailyRank(ranklist)
		# query_result = self.database.findDailyRank({"date": time.strftime("%Y-%m-%d", time.localtime())})
		return sorted_stock_dict, sorted_stock_sentiment_dict

	def caculateMessageScore(self, messages, stock, verbose=False):
		m_score = 0
		watchlist_count = 0
		trending_score = 0
		sentiment_score = 0
		# print(messages.count())
		if messages.count() > 0:
			symbols = dict(messages[0])['symbols']
			watchlist_count = 0
			for symbol in symbols:
				if symbol['symbol'] == stock:
					watchlist_count = symbol['watchlist_count']
					# trending = symbol['trending']
					history_trending_score = symbol['trending_score']
					trending_score = history_trending_score
		for m in messages:
			# pprint.pprint(m)
			m = dict(m)
			# print(m)
			reshared_count = m['reshares']['reshared_count']
			like_count = m['user']['like_count']
			followers = m['user']['followers']
			subscribers_count = m['user']['subscribers_count']
			sentiment = m['entities']['sentiment']
			# print(reshared_count, like_count, followers, sentiment)
			cur_score = 10 + reshared_count + like_count + followers+ subscribers_count*10
			m_score += cur_score
			# print(sentiment)
			if sentiment != None:
				# print(sentiment)
				if sentiment['basic'] == 'Bearish':
					sentiment_score += -10* math.log(cur_score)
				if sentiment['basic'] == 'Bullish':
					sentiment_score += 10* math.log(cur_score)
			# else:
			# 	try:
			# 		messages_body = m['body']
			# 		sentiment = self.sentiment_analysis(messages_body)
			# 		if sentiment[0] == 'neg':
			# 			sentiment_score += -1*sentiment[1]* math.log(cur_score)
			# 		elif sentiment[0] == 'pos':
			# 			sentiment_score += 1*sentiment[2]* math.log(cur_score)
			# 		print(messages_body)
			# 		print(sentiment[0], sentiment[1], sentiment[2])
			# 		if verbose:
			# 			print(messages_body)
			# 			print(sentiment[0], sentiment[1], sentiment[2])
			# 	except:
			# 		print("error with sentiment analysis")

			# print(m_score)
			# break
		return m_score, watchlist_count, trending_score, sentiment_score

	def printTopLists(self, sorted_stock_dict, sorted_stock_sentiment_dict, topN=3):
		re = {"popular":[],"bearish":[],"bullish":[]}
		# print(sorted_stock_dict)
		print("Top " + str(topN) + " popular stocks: ")
		for i in range(topN):
			stock = sorted_stock_dict[i]
			print("stock: " + stock[0] + ", popularity score: " + str(stock[1]))
			re["popular"].append({"name":stock[0],"score":str("%.2f"%stock[1])})

		print("Top " + str(topN) + " Bullish stocks: ")
		for i in range(topN):
			stock = sorted_stock_sentiment_dict[i]
			print("stock: " + stock[0] + ", sentiment score: " + str(stock[1]))
			re["bullish"].append({"name":stock[0],"score":str("%.2f"%stock[1])})

		print("Top " + str(topN) + " Bearish stocks: ")
		for i in range(len(sorted_stock_sentiment_dict)-1, len(sorted_stock_sentiment_dict)-topN-1, -1):
			# print(i)
			stock = sorted_stock_sentiment_dict[i]
			print("stock: " + stock[0] + ", sentiment score: " + str(stock[1]))
			re["bearish"].append({"name":stock[0],"score":str("%.2f"%stock[1])})

	def getTopLists(self, sorted_stock_dict, sorted_stock_sentiment_dict, topN=3):
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
		return re

	def sentiment_analysis(self, sentence):
		blob = TextBlob(sentence, analyzer=NaiveBayesAnalyzer())
		return blob.sentiment

	def get_stock_price(self, stock, start=None, end=None):
		"""get stock price through yahoo finance API"""
		stock = Share(stock)
		if start == None:
			# print(stock.get_open())
			price =  {'Volume': stock.get_volume(), 
			'Adj Close': stock.get_prev_close(), 
			'High': stock.get_days_high(), 
			'Low': stock.get_days_low(), 
			'Open': stock.get_open()}
			return price
		else:
			# print(start, end)
			# pprint.pprint(stock.get_historical(start, end))
			open_price = stock.get_historical(start, end)[0]['Open']
			# print(open_price)
			return open_price

	def get_stock_price_update(self, stock, start=None, end=None):
		if start != None:
			apple = web.DataReader(stock, "yahoo", start, end)
			return apple

	def run_every_hour(self):
		last_time_analyze=int(time.time())
		print("start run_every_hour")
		print(last_time_analyze)
		self.analysisPopularityEveryHour()
		while True:
			# print(int(time.time()))
			if int(time.time())-last_time_analyze >3600:
				try:
					self.analysisPopularityEveryHour()
					# return
				except Exception,e:
					print Exception,e
				last_time_analyze = int(time.time())
					
				time.sleep(1800)

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
			if stock_message.count() == 0:
				stock_message = self.findMessages({'symbols': {'$elemMatch':{'symbol':stock}}})
		elif sentiment >= 0:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}, 'entities':{'sentiment': {'basic': 'Bullish'}}})
			# print(type(stock_message))
			# print(stock_message.count())
			if stock_message.count() == 0:
				stock_message = self.findMessages({'symbols': {'$elemMatch':{'symbol':stock}}})
		else:
			stock_message = self.findMessages({'created_at': {'$gte': start.isoformat(),'$lt':cur_time.isoformat()}, 'symbols': {'$elemMatch':{'symbol':stock}}, 'entities':{'sentiment': {'basic': 'Bearish'}}})
			# print(type(stock_message))
			# print(stock_message.count())
			if stock_message.count() == 0:
				stock_message = self.findMessages({'symbols': {'$elemMatch':{'symbol':stock}}})

		message = []
		for m in stock_message[0:10]:
			cur_m = dict()
			# pprint.pprint(m)
			m = dict(m)
			cur_m['body'] = m['body']
			cur_m['username'] = m['user']['username']
			cur_m['time'] = m['created_at']
			message.append(cur_m)
		return message

			


if __name__ == '__main__':
	analyzer = STAnalysis(database="bigdata")
	# analyzer.analysisPopularityEveryHour()
	"""automatically update the analysis every hour"""
	# analyzer.run_every_hour()

	# cur_hour =  datetime.datetime.now()
	# cl = analyzer.findMessageOneHour(date, cur_hour.hour)
	# date = (2017, '03', 21)
	# cur_time = time.strftime("%Y-%m-%d", time.localtime())
	# print(cur_time)

	"""test yahoo api"""
	# analyzer.get_stock_price('XOM', '2014-04-25', '2014-04-26')
	# start = datetime.datetime(2017, 3, 20)
	# end = datetime.datetime(2017, 3, 30)
	# analyzer.get_stock_price_update('AAPL', start, end)

	"""test sentiment analysis"""
	# sentence = "I love this!"
	# sentiment = analyzer.sentiment_analysis(sentence)
	# print(sentiment[0])
	# print(type(sentiment))
	# date = (2017, '03', 24)
	# cl = analyzer.findMessageOneDay(date)
	# analyzer.caculateMessageScore(cl)


	"""calculate and show daily rank"""
	# cur_hour =  datetime.datetime.now()

	date = (2017, 4, 10)
	cl = analyzer.findMessageOneDay(date) 
	sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)
	analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=5)

	# date = (2017, 3, 31)
	# cl = analyzer.findMessageOneDay(date) 
	# sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)
	# analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=5)

	# date = (2017, 4, 01)
	# cl = analyzer.findMessageOneDay(date) 
	# sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)
	# analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=5)

	# date = (2017, 4, 02)
	# cl = analyzer.findMessageOneDay(date) 
	# sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)
	# analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=5)


	# date = (2017, 4, 03)
	# cl = analyzer.findMessageOneDay(date) 
	# sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)
	# analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=5)


	# """daily rank for current time"""
	# date = (cur_hour.year, cur_hour.month, cur_hour.day)
	# sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, cur_hour.hour)
	# analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=5)

	"""add daily rank to all dates"""
	# """Feb"""
	# for i in range(16, 29):
	# 	date = (2017, '02', i)
	# 	# print(date)
	# 	# cl = analyzer.findMessageOneDay(date)
	# 	sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)
	# 	# analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=5)

	# 	# break

	# """March"""
	# for i in range(1, 31):
	# 	date = (2017, '03', i)
	# 	print(date)
	# 	# cl = analyzer.findMessageOneDay(date)
	# 	sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)
	# 	# sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityOneDay(date, verbose=False)
	# 	# break

	# """April"""
	# for i in range(1, 12):
	# 	date = (2017, '04', i)
	# 	print(date)
	# 	# cl = analyzer.findMessageOneDay(date)
	# 	sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityEveryHour(date, 23, verbose=False)

	"""old version"""
	# sorted_stock_dict, sorted_stock_sentiment_dict = analyzer.analysisPopularityOneDay(date, verbose=True)
	# analyzer.printTopLists(sorted_stock_dict, sorted_stock_sentiment_dict, topN=3)
	
