import json
import os
import tweepy
from typing import List, Dict
import google.generativeai as genai

# Environment variables
TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# Twitter API setup
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(auth)

# Gemini API setup
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_thread_tweets(tweet_id: str) -> List[str]:
    """Fetch all tweets in a thread given the last tweet's ID."""
    tweets = []
    for tweet in tweepy.Cursor(twitter_api.user_timeline, tweet_id=tweet_id, tweet_mode='extended').items():
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if tweet.in_reply_to_status_id_str is None:
                break
        tweets.append(tweet.full_text)
    return list(reversed(tweets))

def summarize_text(text: str) -> str:
    """Use Gemini to summarize the given text."""
    prompt = f"Summarize the following Twitter thread in a concise paragraph:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

def lambda_handler(event: Dict, context: Dict) -> Dict:
    """Main Lambda function handler."""
    try:
        body = json.loads(event['body'])
        tweet_url = body['tweet_url']
        
        # Extract tweet ID from URL
        tweet_id = tweet_url.split('/')[-1]
        
        # Get thread tweets
        tweets = get_thread_tweets(tweet_id)
        
        # Combine tweets into a single text
        full_text = ' '.join(tweets)
        
        # Summarize the text using Gemini
        summary = summarize_text(full_text)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'summary': summary,
                'tweet_count': len(tweets)
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
