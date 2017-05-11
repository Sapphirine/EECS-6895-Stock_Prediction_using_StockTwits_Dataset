# Market-Intelligence-Analysis-Stock-Prediction-using-StockTwits-Dataset

Here are the functionality of each file:
## Final Report
market-intelligence-analysis_final_report_tp2522_jj2860.pdf
## Final Project Slide
EECS6895-AdvancedBigDataAnalytics-Final-Project-tp2522-jj2860.pptx
## flaskapp.py
Script for building our website. 
## StockTwits_Analysis.py
Script for analyzing the popularity and sentiment scores.
## StockTwits_DataCollection.py
Script for automatically collecting the newest StockTwits data
## StockTwits_StockList.py
List of stock that we picked for this project. Because of time and space constrain, we only picked 44 stocks to collect and analyze. Through this script, we can dynamically change the list of stocks. 
## StockTwits_TimeDomainAnalysis.py
Script for gathering and analyzing data in the input time period. User can input the time period that they are interested in by giving start date and end date, and this program will return the corresponding analysis results.
## ProcessStock.py
Process historical data so that it can be used for training machine learning model
## stock_ml.py
Use historical data and new data to create machine learning model
## WebSupport.py
Class we used for real-time analyze and put these analysis onto our website
