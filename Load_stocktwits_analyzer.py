# -*- coding: utf-8 -*-
"""
Created on Tue May  8 22:54:53 2018

@author: Chris
"""

import tweepy
import csv
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
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
        self.datPath = '\\\\192.168.0.24\\SambaPi\\TweetDat_backup\\'
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
            twits = twitapi.get_stock_stream(query, params={})
            
            
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
            bb = bull.append(bear)
            res4 = bb.str.contains('Bullish', na=False, regex=True).astype(int)
                    

            self.data = panda_dict
            self.save_tweets_to_csv()
        except:
            print("API rate limit reached!")  
        data = pd.read_csv(self.datPath+'tweets_'+self.query+'.csv',encoding='utf-8', index_col=None)    
        print ("---------------Data fetching completed!-------------------------") 
        print ("---------------Data set shape: "+ str(data.shape)+ " ----------------------") 
        
        return res4
        
    def save_tweets_to_csv(self):
        # Open/Create a file to append data
        if os.path.exists(self.datPath+'tweets_'+self.query+'.csv'):
            self.data.to_csv(self.datPath+'tweets_'+self.query+'.csv', mode = 'a', encoding='utf-8',index=False, header = None)
            print (str(self.data.shape[0]) + " tweets successfully added to //" + self.datPath+'tweets_'+self.query+'.csv' "// !")
        else:      
            #Use csv Writer
            self.data.to_csv(self.datPath+'tweets_'+self.query+'.csv', encoding='utf-8',index=False)
            print("New csv created!")
            print (str(self.data.shape[0]) + "tweets successfully saved!")
            print ("Path: " + self.datPath+'tweets_'+self.query+'.csv')
            
            
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
        data = pd.read_csv(self.datPath+'tweets_'+self.query+'.csv',encoding='utf-8', index_col=None)
        print("Data set before cleaning: " + str(data.shape)) 
        ## Scan and remove duplicates
       # data_new = data.drop("Unnamed: 0")
        new_data = data.drop_duplicates("Tweets", keep ='first')
        new_data = new_data.dropna(axis=0, how='any',  subset=None, inplace=False)
        print("New data set: " + str(new_data.shape))   
        print("Removed " + str(len(new_data["Tweets"]) - len(data["Tweets"])) + " dupclicates!")
        
        
        new_data.to_csv(self.datPath+'tweets_'+query+'.csv', encoding='utf-8', index=False)
        
        
        return new_data
        
                
                
        


### init 
get_tweet_data = get_tweets()
### fetch data based on query word
#get_tweet_data.fetch_tweets(query='BITCOIN', count=100, pages=1)


#get_tweet_data.fetch_stocktwits(query='BTC.X')
### delete duplicates data from CSV
data = get_tweet_data.clean_data_from_csv(query='stocktwits_BTC.X')
#data = get_tweet_data.data



    

# We extract the tweet with more FAVs and more RTs:

#fav_max = np.max(data['Likes'])
#rt_max  = np.max(data['RTs'])
#
#fav = data[data.Likes == fav_max].index[0]
#rt  = data[data.RTs == rt_max].index[0]
#
## Max FAVs:
#print ("------------------------------------------------------------")
#print("The tweet with more likes is: \n{}".format(data['Tweets'][fav]))
#print("Number of likes: {}".format(fav_max))
#print("{} characters.\n".format(data['len'][fav]))
#print ("------------------------------------------------------------")
#
## Max RTs:
#print ("------------------------------------------------------------")
#print("The tweet with more retweets is: \n{}".format(data['Tweets'][rt]))
#print("Number of retweets: {}".format(rt_max))
#print("{} characters.\n".format(data['len'][rt]))
#print ("------------------------------------------------------------")
#
######
## We extract the mean of lenghts:
#
#mean = np.mean(data['len'])
#print ("------------------------------------------------------------")
#print("The lenght's average in tweets: {}".format(mean))
#print ("------------------------------------------------------------")



# We create time series for data:
data['Date'] = pd.to_datetime(data['time'], errors = 'coerce')
#
#tlen = pd.Series(data=data['len'].values, index=data['Date'])
#tfav = pd.Series(data=data['Likes'].values, index=data['Date'])
#tret = pd.Series(data=data['RTs'].values, index=data['Date']) 
#
#
## Lenghts along time:
##tret.plot(figsize=(16,4), color='r');
##tlen.plot(figsize=(16,4), color='b');





def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing 
    links and special characters using regex.
    '''
    
    if type(tweet) != str:
        print ('No string', tweet)
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def analize_sentiment(tweet):
    '''
    Utility function to classify the polarity of a tweet
    using textblob.
    '''
    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1
    
    
# We create a column with the result of the analysis:
data['SA'] = np.array([ analize_sentiment(tweet) for tweet in data['Tweets'] ])

int_sent = []
for i in data['basic_sentiment']:
   
    if i == 'Bearish':
        int_sent.append(-1)
    elif i == 'Bullish':
        int_sent.append(1)
    elif i == 'None':
        int_sent.append(0)
    else:
        print('ERROR in sentiment conversion')       
            
data['int_sent'] = int_sent      

tsa = pd.Series(data=data['int_sent'].values, index=data['Date']) 


tsa_group =  tsa.groupby(pd.Grouper(freq="H"))  
liste = {}



days = [day for day, group in tsa_group]
print("Amount of days in data set: ", len(days))

### split into day and save to hdf
for day, group in tsa_group:
   liste[day] = group
   get_tweet_data.data = group
   get_tweet_data.save_tweets_to_hdf(str(day))
   print ("Day: " + str(day))
   print ("Number of entries: " , len(liste[day]))
   
   

test = tsa_group.aggregate(np.sum)

pos_res = []
neut_res = []
neg_res =[]
days =[]
len_day_data =[]
for day, day_data in liste.items():
    
#    pos_tweets = [day_data[index] for index in day_data if day_data[index] > 0]
#    neu_tweets = [day_data[index] for index in day_data if day_data[index] == 0]
#    neg_tweets = [day_data[index] for index in day_data if day_data[index] < 0]
    

    neg_tweets = []
    neu_tweets = []
    pos_tweets = []
    
    

    
    for i in day_data:
     #print(i)
     if i < 0:
    
         neg_tweets.append(i)
     elif i == 0:
         neu_tweets.append(i)
     elif i > 0:
         pos_tweets.append(i)
         
    try:    
             # We print percentages:
        print("Time: ", day)
        print("Percentage of positive tweets: {}%".format(len(pos_tweets)*100/len(day_data)))
        print("Percentage of neutral tweets: {}%".format(len(neu_tweets)*100/len(day_data)))
        print("Percentage de negative tweets: {}%".format(len(neg_tweets)*100/len(day_data)))


        pos_res.append(len(pos_tweets)*100/len(day_data)) 
        neut_res.append(len(neu_tweets)*100/len(day_data))
        neg_res.append(len(neg_tweets)*100/len(day_data))
        len_day_data.append(len(day_data))
        days.append(day)    
    except:
        print("day data issue")
results = pd.DataFrame({'pos_tweet' : pos_res, 
                        'neut_tweet': neut_res, 
                        'neg_res' : neg_res, 
                        'days' : days,
                        'len_day_data' : len_day_data})
                
results.to_csv('test_H.csv')      
results['Date'] = pd.to_datetime(results['days'], errors = 'coerce')

data_frame_res = pd.DataFrame( index=results['Date'])
#data_frame_res = data_frame_res.drop('days', axis=1)
for col in list(results):
    
    
    data_frame_res[col] = pd.Series(data=results[col].values, index=results['Date'])


#bull = tlen.loc[tlen[:].isin(['Bullish'])]
#bear = tlen.loc[tlen[:].isin(['Bearish'])]
#bb = bull.append(bear)
#res4 = bb.str.contains('Bullish', na=False, regex=True).astype(int)
#
     
#results.plot()
    
#AO['1980-05':'1981-03'].plot()   
data_frame_res.plot(subplots=True) 
data_frame_res.plot(subplots=False) 
AO_mm = data_frame_res.resample("H").mean()
AO_mm.plot(style='g--')

# We display the updated dataframe with the new column:
#print(data.head(10))   
    
# We construct lists with classified tweets:
#
#pos_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] > 0]
#neu_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] == 0]
#neg_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] < 0]
#
## We print percentages:
#
#print("Percentage of positive tweets: {}%".format(len(pos_tweets)*100/len(data['Tweets'])))
#print("Percentage of neutral tweets: {}%".format(len(neu_tweets)*100/len(data['Tweets'])))
#print("Percentage de negative tweets: {}%".format(len(neg_tweets)*100/len(data['Tweets'])))    