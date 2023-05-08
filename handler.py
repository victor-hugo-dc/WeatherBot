import sys
sys.path.insert(0, 'vendor')

import json
import requests

from dotenv import load_dotenv
import os

load_dotenv()

PREFIX = '^'
FORECAST = PREFIX + 'forecast'
HOURLY = PREFIX + 'hourly'

API_TOKEN = os.environ.get("API_TOKEN")

def receive(event, context):
    message = json.loads(event['body'])

    bot_id = message['bot_id']
    response = process(message)
    if response:
        send(response, bot_id)

    return {
        'statusCode': 200,
        'body': 'ok'
    }


def process(message):
    # Prevent self-reply
    if message['sender_type'] == 'bot':
        return None
    
    if message['text'].startswith(PREFIX):
        location = ' '.join(message['text'].split()[1:])
        url = f'http://api.weatherapi.com/v1/forecast.json?key={API_TOKEN}&q={location}&days=3&aqi=no&alerts=no'
        
        response = requests.get(url)

        if response.status_code != 200:
            return None
        
        response = response.json()

        forecast = response["forecast"]["forecastday"][0]
        reply = "Unsure of that command, try ^forecast <city> or ^hourly <city>."

        if message['text'].startswith(FORECAST):
            daycast = forecast["day"]
            reply = '\n'.join([
                f"{daycast['condition']['text']} with lows of {daycast['mintemp_f']} °F and highs of {daycast['maxtemp_f']} °F",
                f"https:{daycast['condition']['icon']}"
            ])

        if message['text'].startswith(HOURLY):            
            reply = '\n'.join([
                f"{condition['time'].split()[1]}: {condition['temp_f']} °F, {condition['condition']['text']}"
                for condition in forecast["hour"]
            ])

        return reply

def send(text, bot_id):
    url = 'https://api.groupme.com/v3/bots/post'

    message = {
        'bot_id': bot_id,
        'text': text,
    }
    r = requests.post(url, json=message)