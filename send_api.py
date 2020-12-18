import os
import json

import requests


def send_text_message(recipient_id, message, messaging_type='RESPONSE'):
    print(f'SEND_API.SEND_TEXT_MESSAGE({recipient_id}, {message}, {messaging_type})')

    url = os.environ.get('send_api_url')
    params = {
        'access_token': os.environ.get('fb_api_token'),
        'recipient': json.dumps({'id': recipient_id}),
        'message': json.dumps({'text': message})
    }

    response = requests.post(url, params=params)
    print(f'SEND_API_RESPONSE {response}')
