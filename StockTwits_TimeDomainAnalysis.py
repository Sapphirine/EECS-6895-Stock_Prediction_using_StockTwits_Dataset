from StockTwitsDataset import STDataset
import datetime

class QueryTimeDomainData:
	"""docstring for QueryTimeDomainData"""
	def __init__(self, db):
		self.db_name = db

	def queryData(self,start_time,end_time,symbols):
		#check start_time and end_time
		try:
			if start_time > end_time:
				print "TDD -- Time error !"
				return False
		except:
			print "TDD -- Time type error !"
			return False

		try:
			if len(symbols) == 0:
				print "TDD -- No symbols !"
				return False
		except:
			print "TDD -- Symbol List type error !"
			return False
		
		#Get each date point
		oneday = datetime.timedelta(days=1)
		delta = start_time
		time_string_list = []
		while delta<=end_time:
			time_string_list.append(delta.isoformat())
			delta += oneday
		#Query all data from database
		database = STDataset(database = self.db_name)
		daily_data_list = []
		for dt in time_string_list:
			re = database.findDailyRank({"date":dt})
			if type(re) != "NoneType":
				daily_data_list.append(re)
			else:
				daily_data_list.append("Empty")
		
		# print daily_data_list
		result = {}
		for v in symbols:
			result[v] = {"popular":[],"sentiment":[],"price":[]}

		for day in daily_data_list:
			if not day == "Empty":
				#for c in day.items():
					for v in symbols:
						try:
							result[v]["popular"].append(day["popular"][v])
						except:
							result[v]["popular"].append(0)
						
						try:
							result[v]["sentiment"].append(day["sentiment"][v])
						except:
							result[v]["sentiment"].append(0)
						
						try:
							result[v]["price"].append(day["price"][v])
						except:
							result[v]["price"].append({})
							
			else:
				for v in symbols:
					result[v]["popular"].append(0)
					result[v]["sentiment"].append(0)
					result[v]["price"].append({})
		
		return result, time_string_list

			
		#Reformat time domain data

if __name__ == '__main__':
	all_stocks = ['XOM', 'PXD', 'CVX', 'HAL', 'COP', 'FCX', 'X', 'IP', 'LYB', 'VMC', 'GE', 'BA', 'UNP', 'MMM', 'CAT', 'DIS', 'TSLA', 'NFLX', 'ORLY', 'SBUX', 'SPY', 'BAC', 'QQQ', 'JPM', 'C', 'GILD', 'BMY', 'PFE', 'JNJ', 'AMGN', 'AAPL', 'AMZN', 'NVDA', 'CTSH', 'MSFT', 'VZ', 'T', 'CMCSA', 'CTL', 'EXC', 'NEE', 'EIX', 'DUK', 'D']
	ana = QueryTimeDomainData("bigdata")
	print ana.queryData(datetime.date(2017,04,10),datetime.date(2017,04,12),['COP'])
