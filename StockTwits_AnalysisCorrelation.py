from __future__ import division
import time
import datetime
import StockTwits_StockList as STSL
from StockTwits_TimeDomainAnalysis import QueryTimeDomainData
import numpy
import copy

class AnalysisCorrelation:
	def __init__(self):
		self.qtdd = QueryTimeDomainData("bigdata")


	def analysisStockFromDb(self,start_time,end_time,stocks):
		data,tl = self.qtdd.queryData(start_time,end_time,stocks)

		return self.analysisStock(data,stocks)


	def analysisStock(self,data_raw,stocks):
		data = copy.deepcopy(data_raw)
		analysis_result = {}
		#print "\n\n\n\n\n"
		#print(data['X']['popular'])
		#print(data['X']["price"])
		#print(stocks)
		for each in stocks:
			percent_price = []
			popular = data[each]["popular"]
			sentiment = data[each]["sentiment"]
			price = data[each]["price"]
			#print price
			# i = 0
			# while (i<len(price)):
			# 	if price[i] == None :
			# 		del price[i]
			# 		del popular[i]
			# 		del sentiment[i]
			# 	else:
			# 		i = i+1
			
			
			
			for i in range(len(price)-1):
				percent = 0
				try:
					if price[i] == None or price[i+1] == None:
						percent_price.append(0)
					else:
						price1 = float(str(price[i]["Adj Close"]))
						price2 = float(str(price[i+1]["Adj Close"]))
						print price1,price2
						#percent = (price[i+1]["Adj Close"] - price[i]["Adj Close"])/price[i]["Adj Close"]*100
						percent = (price2 - price1)*100/price1
						percent_price.append(percent)
				except Exception,e:
					print "data exception : " + str(i)
					print e
					percent_price.append(0)
					pass
			
			del popular[-1]
			del sentiment[-1]

			i = 0
			while (i<len(percent_price)):
				if percent_price[i] == 0 :
					del percent_price[i]
					del popular[i]
					del sentiment[i]
				else:
					i = i+1

			s = 0
			p = 0
			for i in range(len(percent_price)):
				s += 1
				if (percent_price[i] * sentiment[i] > 0):
					p+=1

			print("\n\nin predict\n\n")
			print(popular)
			#print sentiment
			#print price
			kk = numpy.corrcoef([popular,sentiment,percent_price])
			analysis_result[each] = {"popular":popular, "sentiment":sentiment, "variation":percent_price, "corrcoef":kk,"predict":0}
			if (s>0):
				analysis_result[each]["predict"] = p*100/s
		return analysis_result

if __name__ == "__main__":
	print("start data collection")
	anas = AnalysisCorrelation()
	res = anas.analysisStockFromDb(datetime.date(2017,03,15),datetime.date(2017,04,12),STSL.ALL_LIST)
	outfile = open("stock_analysis_result.csv","w")
	outfile.write("symble,corr vs pop,corr vs senti,predict\n")
	for each in STSL.ALL_LIST:
		try:
			print each
			outfile.write(each+",")
			outfile.write(str(res[each]["corrcoef"][2][0])+",")
			outfile.write(str(res[each]["corrcoef"][2][1])+",")
			outfile.write(str(res[each]["predict"])+"\n")
		except:
			outfile.write("\n")
			pass
	outfile.flush()
	outfile.close()
