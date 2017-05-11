import flask
import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap 
from StockTwitsDataset import STDataset
from StockTwits_TimeDomainAnalysis import QueryTimeDomainData
from StockTwits_AnalysisCorrelation import AnalysisCorrelation
import StockTwits_StockList as STSL
from WebSupport import TempClass
import copy


app = Flask(__name__)
Bootstrap(app)

@app.route("/",methods=['POST', 'GET'])
def firstPage():
	context = dict()
	fun = TempClass()
	top_lists = fun.get_top_lists()
	context['top_lists'] = top_lists
	context['topLen'] = len(top_lists['popular'])
	return render_template("index.html", **context)


@app.route("/stock/symbol/<stock_name>",methods=['POST', 'GET'])
def stock(stock_name):
	context = dict()
	fun = TempClass()
	top_lists = fun.get_top_lists()
	data, time_string_list = fun.get_time_query()
	context['sentiment'] = str("%.2f"%data[stock_name]['sentiment'][-1])
	message = fun.get_messages(stock_name, context['sentiment'])
	context['stock_name'] = stock_name
	context['total_data'] = data
	context['close_price'],  weekend_index = fun.get_close_price(data, stock_name)
	context['predict'] =  str("%.2f"%fun.get_predict(data, [stock_name])[stock_name]['predict'])
	del time_string_list[weekend_index[0]]
	del time_string_list[weekend_index[1]-1]
	popular_list = data[stock_name]['popular']
	del popular_list[weekend_index[0]]
	del popular_list[weekend_index[1]-1]
	sentiment_list = data[stock_name]['sentiment']
	del sentiment_list[weekend_index[0]]
	del sentiment_list[weekend_index[1]-1]
	context['popular_list'] = popular_list
	context['sentiment_list'] = sentiment_list
	context['labels'] = time_string_list
	context['message'] = message
	context['top_lists'] = top_lists
	context['popular'] = str("%.2f"%data[stock_name]['popular'][-1])
	return render_template("stock.html", **context)


if __name__ == "__main__":	
	# app.debug = True
	# app.run(host='0.0.0.0',port=8050)

	fun = TempClass()
	data, time_string_list = fun.get_time_query()
	predict = fun.get_predict(data, ['X'])
	# close_price,  weekend_index = fun.get_close_price(data, 'JPM')
	# print(data['JPM'])
	# print(time_string_list)
	# print(weekend_index)
	# del time_string_list[weekend_index[0]]
	# del time_string_list[weekend_index[1]-1]
	# print(time_string_list)
	# query_date = "2017-04-12"
	# get_top_lists()
	# get_time_query()
	# get_messages('COP', -1)
	# data, time_string_list = get_time_query()
	# print(data['AAPL'])
	# anas = AnalysisCorrelation()
	# prediect = anas.analysisStock(data, STSL.ALL_LIST)
	# print(prediect['COP']['predict'])
	# print(data['COP']['price'])
	# close_list = []
	# for i in data['COP']['price']:
	# 	print(i)
	# 	close = i['Adj Close']
	# 	close_list.append(close)
	# popular_time = get_popular_time(data, time_string_list)
