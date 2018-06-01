# -*- coding: utf-8 -*-
"""
Created on Tue May  8 22:54:53 2018

@author: Chris
"""

import tweepy

import pandas as pd
import numpy as np
from textblob import TextBlob

import os

from datetime import timedelta
import dateutil.parser

## stocktwit api
import api as twitapi

class get_tweets:
    
    def __init__(self, 
                 consumer_key = 'edxIg10mLXYvXfFy6YcL9Ljlf',
                 consumer_secret= 'a6ulFtT7UAKxRfrqPb4KKklhTtaeBhpjXFsiz31WnfmAHAxLut',
                 access_token='55509426-JHSDeISdoOgc3GZfLmOhJix9gGB9yKexccVKuA38X',
                 access_token_secret='crlpWSek13UjtDM6HMqwuJyGMPXbvy1MkQo6bssU0n0JN'
                 ):
       
      
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        #Path to store cached currency data
        self.datPath = 'TweetDat/'
        if not os.path.exists(self.datPath):
            os.mkdir(self.datPath)
        self.query = None    
        self.data = None

    def fetch_tweets(self, query='BITCOIN' , count = 100, pages = 1):
        
        self.query = 'BITCOIN'
       # tweet_list = []
 
        page_count = 1  

        api = tweepy.API(self.auth)


        
        print ("---------------Start fetching new twitter data----------------------")
        
        try:
            for tweets in tweepy.Cursor(api.search, 
                                        q=query, 
                                        count=count,
                                        result_type="recent", 
                                        lang="en",
                                        include_entities=True).pages():  
                    
                    page_count += 1  
                    
                    print("Twitter page: ", page_count)
                    # print just the first tweet out of every page of 100 tweets  
                    #print (tweets[0].text.encode('utf-8') ) 
                    
                    
                    for i in range(len(tweets)):
                        
                    #    tweet_list.append(tweets[i].text)          
                    
                    # We create a pandas dataframe as follows:    
                    ### panda frames    
                        
                        self.data = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
                        self.data['len']  = np.array([len(tweet.text) for tweet in tweets])
                        self.data['ID']   = np.array([tweet.id for tweet in tweets])
                        self.data['Date'] = np.array([tweet.created_at for tweet in tweets])
                        self.data['Source'] = np.array([tweet.source for tweet in tweets])
                        self.data['Likes']  = np.array([tweet.favorite_count for tweet in tweets])
                        self.data['RTs']    = np.array([tweet.retweet_count for tweet in tweets])
                        
                        self.data['name'] = np.array([tweet.user.name for tweet in tweets])
                        self.data['location'] = np.array([tweet.user.location for tweet in tweets])
                              
                        self.data['friends_count'] = np.array([tweet.user.friends_count for tweet in tweets])
                        self.data['favourites_count'] = np.array([tweet.user.favourites_count for tweet in tweets])
                     
                        self.data['followers_count'] = np.array([tweet.user.followers_count for tweet in tweets])
                                        
                        
                        # stop after retrieving 200 pages  
                        
                        ### save data to csv
                        self.save_tweets_to_csv()
                           
                        if page_count > pages:  
                                break   
                            
                        
        except:
            print("API rate limit reached!")  
        data = pd.read_csv(self.datPath+'tweets_'+query+'.csv',encoding='utf-8', index_col=None)    
        print ("---------------Data fetching completed!-------------------------") 
        print ("---------------Data set shape: "+ str(data.shape)+ " ----------------------") 



    def fetch_stocktwits(self, query='BTC.X'):
        self.query = 'stocktwits_' + query
        
        print ("--------------Start fetching new stocktwit data---------------------")
    
        try:
            twits = twitapi.get_stock_stream(query, params={'limit' : 3})
            
            '''Parameters
            id:	Ticker symbol, Stock ID, or RIC code of the symbol (Required)
            since:	Returns results with an ID greater than (more recent than) the specified ID.
            max:	Returns results with an ID less than (older than) or equal to the specified ID.
            limit:	Default and max limit is 30. This limit must be a number under 30.
            callback:	Define your own callback function name, add this parameter as the value.
            filter:	Filter messages by links, charts, videos, or top. (Optional)
            '''    
            messages = []
    
            messages = twits['messages']
            
                
            body = []   
            symbols = []
            id_mes = []
            mentioned_users = []
            source =[]
            conversation = []
            chart = []
            entities =[]
            basic_sentiment = []
            date = []
            com_dict = {'body' : body , 'symbols' : symbols , 'id' : id_mes,
                        'mentioned_users' : mentioned_users, 'source' : source,
                        'conversation' : conversation, 'entities' : entities,
                        }
                
            
            for i in range(len(messages)): 
                
            
            
                for item in com_dict.items():
                    try:
                        item[1].append(messages[i][item[0]])
                        
                        
                    except:
                         item[1].append('None')
            
            
            
                try:
                    basic_sentiment.append(messages[i]['entities']['sentiment']['basic'])
                except:
                    basic_sentiment.append('None')
                    #print('No basic_sentiment')
                    
                try:
                    chart.append(messages[i]['entities']['chart'])
                except:
                    chart.append('None')
                    #print('No chart')  
                    
                try:
                    d = dateutil.parser.parse(messages[i]['created_at'])
                    date.append(d.strftime('%m/%d/%Y %H:%M'))
                except:
                    date.append('None')        
                    
               
            dict_two = {'basic_sentiment' : basic_sentiment, 'chart' : chart, 'time' : date}
            com_dict.update(dict_two)
            
            panda_dict =  pd.DataFrame.from_dict(com_dict)   
            panda_dict['time'] = pd.to_datetime(panda_dict['time'])
            panda_dict.rename(columns={'body': 'Tweets'}, inplace=True)
            ## extract sentiment
            tlen = pd.Series(data=panda_dict['basic_sentiment'].values, index=panda_dict['time'])
            bull = tlen.loc[tlen[:].isin(['Bullish'])]
            bear = tlen.loc[tlen[:].isin(['Bearish'])]
            #bb = bull.append(bear)
            #res4 = bb.str.contains('Bullish', na=False, regex=True).astype(int)
                    
            print('Bullish sentiment for last fetch: ', len(bull)/len(tlen))
            print('Bearish sentiment for last fetch: ', len(bear)/len(tlen))
            print('Twits: ', panda_dict['Tweets'])
            
            
            self.data = panda_dict
            self.save_tweets_to_csv()  
            
            data = pd.read_csv(self.datPath+'tweets_'+self.query+'.csv',encoding="utf-8", index_col=None)    
            print ("---------------Data fetching completed!-------------------------") 
            print ("---------------Data set shape: "+ str(data.shape)+ " ----------------------") 
            print('------------------------------------------------')
            print('------------------------------------------------')
            print('------------------------------------------------')
        except:
            print("API rate limit reached!")
            print('------------------------------------------------')
            print('------------------------------------------------')
            print('------------------------------------------------')
            
            

        
        
        
    def save_tweets_to_csv(self):
        # Open/Create a file to append data
        if os.path.exists(self.datPath+'tweets_'+self.query+'.csv'):
            
            
            read_data = pd.read_csv(self.datPath+'tweets_'+self.query+'.csv',encoding='ISO-8859-1', index_col=None)
            print("Data set before cleaning & merging: " + str(read_data.shape)) 
            ## Scan and remove duplicates
       
            new_data = self.data.drop_duplicates("id", keep ='first')
            print("Removed " + str(len(self.data["Tweets"]) - len(new_data["Tweets"])) + " dupclicates!")
            ## 
            added = []
            for index, row in new_data.iterrows():
               
               bool_array = read_data['id'].isin([row['id']])  
               if np.count_nonzero(bool_array) is 0:
                   added.append(row)
                   print('------------------------------------------------')
                   print('Append ' + str(row) + ' to csv file...')
                   print('------------------------------------------------')
                   print("\n")
                   print("\n")
                   
                   
            panda_dict =  pd.DataFrame.from_dict(added)   
            with open(self.datPath+'tweets_'+self.query+'.csv', 'a') as f:
               
               panda_dict.to_csv(f, header=False ,encoding="utf-8",index=False)
               print('Done.')
               print('------------------------------------------------')
         
            read_data = pd.read_csv(self.datPath+'tweets_'+self.query+'.csv',encoding="utf-8", index_col=None)

            print (str(len(added)) + " tweets successfully added to //" + self.datPath+'tweets_'+self.query+'.csv' "// !")
            print("Size of new data set: " + str(len(read_data))) 
            print('------------------------------------------------')
            print('------------------------------------------------')
            print('------------------------------------------------')
            print("\n")
            print("\n")
            
        else:      
            #Use csv Writer
            self.data.to_csv(self.datPath+'tweets_'+self.query+'.csv', encoding="utf-8",index=False)
            print("New csv created!")
            print (str(self.data.shape[0]) + " tweets successfully saved!")
            print ("Path: " + self.datPath+'tweets_'+self.query+'.csv')
            print('------------------------------------------------')
            print('------------------------------------------------')
            print('------------------------------------------------')
            print("\n")
            print("\n")
            
            
    def save_tweets_to_hdf(self, day):
        # Open/Create a file to append data
        if os.path.exists(self.datPath+'tweets_'+self.query+'.h5'):
            self.data.to_hdf(self.datPath+'tweets_'+self.query+'.h5', key=day, mode='a')
            print (str(self.data.shape[0]) + " tweets successfully added to //" + self.datPath+'tweets_'+self.query+'.h5' "// !")
        else:      
            #Use hdf Writer
            self.data.to_hdf(self.datPath+'tweets_'+self.query+'.h5',key=day)
            print("New hdf5 created!")
            print (str(self.data.shape[0]) + "tweets successfully saved!")
            print ("Path: " + self.datPath+'tweets_'+self.query+'.h5')       
            
            
            
            
    def clean_data_from_csv(self, query):
        self.query = query
        data = pd.read_csv(self.datPath+'tweets_'+self.query+'.csv',encoding="utf-8", index_col=None)
        print("Data set before cleaning: " + str(data.shape)) 
        ## Scan and remove duplicates
       # data_new = data.drop("Unnamed: 0")
        new_data = data.drop_duplicates("id", keep ='first')
       # new_data = new_data.dropna(axis=0, how='any', thresh = 3,  subset=None, inplace=False)
        print("New data set: " + str(new_data.shape))   
        print("Removed " + str(len(new_data["Tweets"]) - len(data["Tweets"])) + " dupclicates!")
        
        
        new_data.to_csv(self.datPath+'tweets_'+self.query+'.csv', encoding="utf-8", index=False)
        
        
        return new_data
        
                
def main():                
    ### init 
    get_tweet_data = get_tweets()
    ### fetch data based on query word
    get_tweet_data.fetch_stocktwits(query='BTC.X')
    ### delete duplicates data from CSV
  #  get_tweet_data.clean_data_from_csv(query='stocktwits_BTC.X')                 
     
 #   get_tweet_data.save_tweets_to_hdf('test')


import time
if __name__ == "__main__":
    loop = True  
    while loop:

        try:
            print("Start main()..")
            print (time.strftime("%H:%M:%S"))
            main()
            
            print("\n")
            print("Waiting...")
            print (time.strftime("%H:%M:%S"))
            print("\n")
            print("\n")
            time.sleep(30)
        except KeyboardInterrupt:
            print (time.strftime("%H:%M:%S"))
            confirm = input('Enter "yes" to cancel or "no" to keep running [yes/no]:').strip().lower()
            if confirm == 'yes':
                loop = False
            else:
                loop = True