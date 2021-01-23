import tweepy
import json, os, requests, time
from dotenv import load_dotenv
from random import randrange

load_dotenv(override=True)

def load_tweets():
    """
    Download all tweets from S3 bucket
    """
    tweets_url = os.environ.get('TWEETS_URL')
    return json.loads(requests.get(tweets_url).text)

def make_tweet(tweet):
    """
    Authenticate against pupppu1 twitter account
    Make tweet
    """
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(
        os.environ.get('API_KEY'), 
        os.environ.get('API_SECRET')
    )
    auth.set_access_token(
        os.environ.get('ACCESS_TOKEN'), 
        os.environ.get('ACCESS_TOKEN_SECRET')
    )

    # Create API object
    api = tweepy.API(auth)

    api.update_status(tweet)
    print(tweet)


if __name__ == "__main__":

    FREQ = 60*60  # seconds per tweet

    while True:

        tweets = load_tweets()
        random_tweet = tweets[randrange(len(tweets))]
        make_tweet(random_tweet)
        time.sleep(FREQ)
