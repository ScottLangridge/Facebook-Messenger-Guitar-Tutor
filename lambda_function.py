import os
import json
import re

import send_api
import database_access


def lambda_handler(event, context):
    print(f'EVENT {json.dumps(event)}')

    http_verb = event['requestContext']['http']['method']
    if http_verb == 'GET':
        return verify_webhook(event)
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

    if 'text' in message.keys():
        msg_txt = message['text']

        # Metronome
        if 'metronome' in msg_txt.lower():
            numeric = re.compile(r'\d+')
            numeric_sections = numeric.findall(msg_txt)

            if len(numeric_sections) != 1:
                invalid_bpm_msg = 'Please include a single number in messages asking for a metronome to indicate bpm.'
                send_api.send_text_message(sid, invalid_bpm_msg)
                return

            bpm = int(numeric_sections[0])
            if 30 > bpm > 400:
                invalid_bpm_msg = 'Please select a bpm between 30 and 400.'
                send_api.send_text_message(sid, invalid_bpm_msg)
                return

            rounded_bpm = str(5 * round(bpm / 5))
            metronome_url = database_access.fetch_resource_url('metronome', rounded_bpm)

            send_api.send_text_message(sid, f'Here is a {rounded_bpm} bpm metronome:\n{metronome_url}')

        # Help
        elif 'help' in msg_txt.lower():
            send_api.send_text_message(sid, 'I can currently do the following:'
                                            '\n  - Get metronomes between 30 and 400 bpm (to the nearest 5 bpm)')
        # Not Recognised
        else:
            send_api.send_text_message(sid, 'I did not understand your message. You can write "help" to see what '
                                            'messages I will understand.')
