# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 17:34:45 2018

@author: Chris
"""

import Load_Tweets_Class
import time


def main():                
    ### init 
    get_tweet_data = Load_Tweets_Class.get_tweets(
                 folder='TweetDat/',
                 consumer_key = 'edxIg10mLXYvXfFy6YcL9Ljlf',
                 consumer_secret= 'a6ulFtT7UAKxRfrqPb4KKklhTtaeBhpjXFsiz31WnfmAHAxLut',
                 access_token='55509426-JHSDeISdoOgc3GZfLmOhJix9gGB9yKexccVKuA38X',
                 access_token_secret='crlpWSek13UjtDM6HMqwuJyGMPXbvy1MkQo6bssU0n0JN')
    
    ### fetch data based on query word
    get_tweet_data.fetch_stocktwits(query='BTC.X')
    ### delete duplicates data from CSV
    get_tweet_data.read_and_clean_data_from_csv(query='stocktwits_BTC.X')                 
     
   # get_tweet_data.save_tweets_to_hdf('test', format = 'table')


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