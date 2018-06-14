# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 17:30:55 2018

@author: Chris
"""


import Load_Tweets_Class
import time
import numpy as np

def main():                
    ### init 
    get_Twitter_data = Load_Tweets_Class.get_tweets(
                 folder='TweetDat/',
                 consumer_key = 'edxIg10mLXYvXfFy6YcL9Ljlf',
                 consumer_secret= 'a6ulFtT7UAKxRfrqPb4KKklhTtaeBhpjXFsiz31WnfmAHAxLut',
                 access_token='55509426-JHSDeISdoOgc3GZfLmOhJix9gGB9yKexccVKuA38X',
                 access_token_secret='crlpWSek13UjtDM6HMqwuJyGMPXbvy1MkQo6bssU0n0JN')
    
    ### fetch data based on query word
    get_Twitter_data.fetch_tweets(query='BITCOIN', count=100, pages=12)
    

    data = get_Twitter_data.data
    
    
    
        
    
   #  We extract the tweet with more FAVs and more RTs:
    
    fav_max = np.max(data['Likes'])
    rt_max  = np.max(data['RTs'])
#    
    fav = data[data.Likes == fav_max].index[0]
    rt  = data[data.RTs == rt_max].index[0]
    
    # Max FAVs:
    print ("------------------------------------------------------------")
    print("The tweet with more likes is: \n{}".format(data['Tweets'][fav]))
    print("Number of likes: {}".format(fav_max))
    print("{} characters.\n".format(data['len'][fav]))
    print ("------------------------------------------------------------")
    
    # Max RTs:
    print ("------------------------------------------------------------")
    print("The tweet with more retweets is: \n{}".format(data['Tweets'][rt]))
    print("Number of retweets: {}".format(rt_max))
    print("{} characters.\n".format(data['len'][rt]))
    print ("------------------------------------------------------------")
    
    #####
    # We extract the mean of lenghts:
    
    mean = np.mean(data['len'])
    print ("------------------------------------------------------------")
    print("The lenght's average in tweets: {}".format(mean))
    print ("------------------------------------------------------------")
    
#    
#        ## delete duplicates data from CSV
#    get_Twitter_data.read_and_clean_data_from_csv(query='BITCOIN')         
#    
#    # We display the updated dataframe with the new column:
#    print(data.head(10))   
#        
#  #   We construct lists with classified tweets:
#    
#    pos_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] > 0]
#    neu_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] == 0]
#    neg_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] < 0]
#    
#    # We print percentages:
#    
#    print("Percentage of positive tweets: {}%".format(len(pos_tweets)*100/len(data['Tweets'])))
#    print("Percentage of neutral tweets: {}%".format(len(neu_tweets)*100/len(data['Tweets'])))
#    print("Percentage de negative tweets: {}%".format(len(neg_tweets)*100/len(data['Tweets'])))                  
        
if __name__ == "__main__":
    loop = True  
    while loop:

        try:
            print("Start main()..")
            print (time.strftime("%H:%M:%S"))
            try:
                main()
            except:
                print("ERROR: main()")
            
            print("\n")
            print("Waiting...")
            print (time.strftime("%H:%M:%S"))
            print("\n")
            print("\n")
            '''
            15 Minute Windows
            Rate limits are divided into 15 minute intervals. All endpoints require authentication, so there is no concept of unauthenticated calls and rate limits.
            
            There are two initial buckets available for GET requests: 15 calls every 15 minutes, and 180 calls every 15 minutes.
            '''
            
            time.sleep(60*1+1) ## per minute
        except KeyboardInterrupt:
            print (time.strftime("%H:%M:%S"))
            confirm = input('Enter "yes" to cancel or "no" to keep running [yes/no]:').strip().lower()
            if confirm == 'yes':
                loop = False
            else:
                loop = True