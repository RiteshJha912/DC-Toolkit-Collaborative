import tweepy

# Set your API keys and access tokens
access_token = '1697243533047201792-ZHcVwABDsysUoIouwVZTR69dEyvPEr'
access_token_secret = 'ezN0HxPFDbipGBXFaIpMA7nhBwIr4XO52OKBcrDcbqyJ6'
api_key = 'E2R999RQOlnPsYI5D1ckRamZR'
api_key_secret = '8S7cbZvtAhBLsawCTetraMLfju5XP6O9DnhlE0odrSu6aFQB5w'

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Specify the username of the target user
username = 'elonmusk'

# Fetch user's tweets
tweets = api.user_timeline(screen_name=username, count=20, tweet_mode="extended")

# Print tweets
for tweet in tweets:
    print(tweet.full_text)