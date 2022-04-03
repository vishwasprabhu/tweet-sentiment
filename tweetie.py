import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dateutil.parser import parse

def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(',')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    items = loadkeys(twitter_auth_filename)
    consumer_key = items[0]
    consumer_secret = items[1]
    access_token = items[2]
    access_token_secret = items[3]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    analyser = SentimentIntensityAnalyzer()
    tweets = []

    for status in tweepy.Cursor(api.user_timeline, screen_name=name).items(100):
        tweets.append({
            'id': status._json['id'],
            'created': status._json['created_at'],
            'retweeted': status._json['retweet_count'],
            'text': status._json['text'],
            'hashtags': [a['text'] for a in status._json['entities']['hashtags']],
            'urls': [a['url'] for a in status._json['entities']['urls']],
            'mentions': [a['screen_name'] for a in status._json['entities']['user_mentions']],
            'score': analyser.polarity_scores(status._json['text'])['compound']
        })
    user = {
        'user': name,
        'count': len(tweets),
        'tweets': tweets
    }
    return user

def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get the list of User objects back from friends();
    get a maximum of 100 results. Pull the appropriate values from
    the User objects and put them into a dictionary for each friend.
    """
    #user = api.get_user(screen_name = name)
    friends = api.get_friends(screen_name = name, count=100)
    friend_lst = []
    for friend in friends:
        friend_lst.append({
                'name': friend._json['name'],
                'screen_name': friend._json['screen_name'],
                'followers': friend._json['followers_count'],
                'created': parse(friend._json['created_at']).strftime('%Y-%m-%d'),
                'image': friend._json['profile_image_url']
        })
    return friend_lst
