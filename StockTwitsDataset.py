'''
Created on Feb 5, 2017

@author: kekedou
'''
from pymongo import MongoClient
import time
timestamp = int(time.time())
#client = MongoClient("mongodb://user1:abcd1234@45.33.45.39:27017/bigdata")
#db = client.bigdata
#co = db.collect1

class STDataset:
    def __init__(self,database,user=None,pwd=None,url=None):
        try:
            self.db_client = MongoClient("mongodb://localhost:27017/"+database)
            #self.db_client = MongoClient("mongodb://"+user+":"+pwd+"@"+url+":27017"+"/"+database)
            self.db = self.db_client.bigdata
            self.message_collection = self.db.messages
            self.user_collection = self.db.users
            self.stock_collection = self.db.stock
            self.stock_daily_collection = self.db.stock_daliy
            self.stock_daily_rank = self.db.rank_daily
        except Exception,e:
            print e
            print "Error during MongoDB init ... "
    
    def saveUsers(self,query):
        successes = []
        for vs in query:
            try:
                if self.saveOneUser(vs):
                    successes.append(vs)
            except:
                pass             
        return successes
    
        
    def saveOneUser(self,query):
        try:
            check = {}
            check["id"] = query["id"]
            query["update_unix_time"] = int(time.time())
            re = self.findOneUser(check)
            try:
                last_time = re["update_unix_time"]
            except:
                last_time = 0
            if re == None:
                self.user_collection.insert(query)
                return True
            elif query["update_unix_time"] - last_time > 360:
                self.user_collection.update(check,query)
                return True
            return False
        except Exception,e:
            print "Error during insert an user ..."
            print Exception,e
            return False   
            
    def findUsers(self,query=None):
        try:
            outs = self.user_collection.find_one(query)
            return outs
        except Exception,e:
            "Error during find an user ..."
            print Exception,e
            return False
    
    def findOneUser(self,query=None):
        try:
            outs = self.user_collection.find_one(query)
            return outs
        except Exception,e:
            "Error during find users ..."
            print Exception,e
            return False
    
    def saveMessages(self,query):
        successes = []
        for vs in query:
            try:
                if self.insertOneMessage(vs):
                    successes.append(vs)
            except:
                pass             
        return successes
    
    def insertOneMessage(self,query):
        try:
            check = {}
            check["id"] = query["id"]
            if self.findOneMessage(check) == None:
                self.message_collection.insert(query)
                return True
            return False
        except Exception,e:
            print "Error during insert a message ..."
            print Exception,e
            return False
        
    def findOneMessage(self,query=None):
        try:
            outs = self.message_collection.find_one(query)
            return outs
        except Exception,e:
            "Error during find message ..."
            print Exception,e
            return None
    
    def findMessages(self,query=None):
        try:
            outs = self.message_collection.find(query)
            return outs
        except Exception,e:
            "Error during find messages ..."
            print Exception,e
            return None
        
    def saveStockRecords(self,query):
        successes = []
        for vs in query:
            if self.saveOneStockRecord(vs):
                successes.append(vs)
        return successes
    
    def saveOneStockRecord(self,query):
        try:
            check = {}
            check["id"] = query["id"]
            query["update_unix_time"] = int(time.time())
            re = self.findLatestStockRecord(check)
            try:
                last_time = re["update_unix_time"]
            except:
                last_time = 0
            if re == None:
                self.stock_collection.insert_one(query)
                #print query["symbol"] + "  stock insert"
                #self.stock_daily_collection.insert_one(query)
                return True
            elif query["update_unix_time"] - last_time > 360:
                self.stock_collection.update(check,query)
                #print query["symbol"] + "  stock update"
                #self.stock_daily_collection.insert_one(query)
                return True
            return False
        except Exception,e:
            print "Error during insert an stock ..."
            print Exception,e
            return False 
        
    def findLatestStockRecord(self,query):
        try:
            outs = self.stock_collection.find_one(query)
            return outs
        except Exception,e:
            "Error during find stock ..."
            print Exception,e
            return None 
    
    def saveDailyRank(self,query):
        try:
            check = {"date":query["date"]}
            c = self.findDailyRank(check)
            if c:
                self.stock_daily_rank.update(check,query)
            else:
                self.stock_daily_rank.insert(query)
            return True
        except Exception,e:
            print Exception,e
            print "Error during save rank ... "      
            return False

    def findStockRecords(self,query):
        try:
            outs = self.stock_daily_collection.find(query)
            return outs
        except Exception,e:
            "Error during find stock ..."
            print Exception,e
            return None
            

    def findDailyRank(self,query):
        try:
            # print(query)
            c = self.stock_daily_rank.find_one(query)
            return c
        except Exception,e:
            print e
            print "Error during search rank ... "
            return None
    
    
if __name__ == '__main__':
    database = STDataset("user1","abcd1234","45.33.45.39","bigdata")
    cl = database.findMessages()
    database.findDailyRank("2017-04-11")