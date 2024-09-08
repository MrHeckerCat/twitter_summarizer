import json
import os
import requests
from typing import Dict, List
import google.generativeai as genai
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RAPIDAPI_KEY = os.environ['RAPIDAPI_KEY']
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# Gemini API setup
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_full_texts(data: Dict) -> List[str]:
    """Recursively extract all 'full_text' values from the response."""
    texts = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'full_text':
                texts.append(value)
            elif isinstance(value, (dict, list)):
                texts.extend(extract_full_texts(value))
    elif isinstance(data, list):
        for item in data:
            texts.extend(extract_full_texts(item))
    return texts

def get_tweet_texts(tweet_id: str) -> str:
    """Fetch tweet texts using RapidAPI."""
    url = "https://twitter-api47.p.rapidapi.com/v2/tweet/details"
    querystring = {"tweetId": tweet_id}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "twitter-api47.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        logger.info(f"Successfully fetched tweet: {tweet_id}")
        
        # Extract all full_text values
        all_texts = extract_full_texts(data)
        
        if not all_texts:
            logger.warning(f"Could not find any tweet texts for tweet {tweet_id}")
            return ''
        
        # Combine all texts into a single paragraph
        combined_text = ' '.join(all_texts)
        logger.info(f"Combined text length: {len(combined_text)}")
        
        return combined_text
    except requests.RequestException as e:
        logger.error(f"Error fetching tweet {tweet_id}: {str(e)}")
        return ''

def summarize_text(text: str) -> str:
    """Use Gemini to summarize the given text."""
    if not text:
        return "No text to summarize."
    prompt = f"Summarize the following Twitter thread in a concise paragraph:\n\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error in text summarization: {str(e)}")
        return "Unable to summarize the text due to an error."

def lambda_handler(event: Dict, context: Dict) -> Dict:
    """Main Lambda function handler."""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        body = json.loads(event['body'])
        tweet_url = body['tweet_url']
        
        # Extract tweet ID from URL
        tweet_id = tweet_url.split('/')[-1]
        logger.info(f"Extracted tweet ID: {tweet_id}")
        
        # Get combined tweet texts
        combined_text = get_tweet_texts(tweet_id)
        
        if not combined_text:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Unable to fetch any tweet texts. The tweet may not exist or be private.'}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        # Summarize the text using Gemini
        summary = summarize_text(combined_text)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'summary': summary,
                'combined_text': combined_text  # Including original combined text for reference
            }),
            'headers': {'Content-Type': 'application/json'}
        }
    except json.JSONDecodeError:
        logger.error("Invalid JSON in the event body")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except KeyError as e:
        logger.error(f"Missing key in request: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing required field: {str(e)}'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An unexpected error occurred'}),
            'headers': {'Content-Type': 'application/json'}
        }
