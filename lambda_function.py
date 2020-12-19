import os
import json

import send_api


def lambda_handler(event, context):
    print(f'EVENT {json.dumps(event)}')

    http_verb = event['requestContext']['http']['method']
    if http_verb == 'GET':
        verify_webhook(event)
    elif http_verb == 'POST':
        content = json.loads(event['body'])
        for entry in content['entry']:
            handle_entry(entry)
        return {'statusCode': 200}
    else:
        return {'statusCode': 500}


def verify_webhook(event):
    # Verify Callback Token
    query_string = event['queryStringParameters']

    try:
        mode = query_string['hub.mode']
        token = query_string['hub.verify_token']
        challenge = query_string['hub.challenge']

        assert mode == 'subscribe'
        assert token == os.environ.get('verify_token')

    except (KeyError, AssertionError) as e:
        print(f'Error when verifying query string: {e}')
        return {'statusCode': 403, 'body': 'Forbidden'}

    return {'statusCode': 200, 'body': challenge}


def handle_entry(entry):
    event_content = entry['messaging'][0]
    if 'message' in event_content.keys():
        handle_message_received(entry)


def handle_message_received(entry):
    event_content = entry['messaging'][0]
    sid = event_content['sender']['id']
    message = event_content['message']

    if 'text' in message.keys() and message['text'].lower().startswith('dev echo '):
        send_api.send_text_message(sid, f'You asked me to echo the following:\n{message["text"][10:]}')
