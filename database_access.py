import boto3


def fetch_item(resource_type, name):
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table('GuitarTutorResources')

    resp = table.get_item(Key={"type": resource_type, "name": name})

    return resp['Item']


def fetch_resource_url(resource_type, name):
    return fetch_item(resource_type, name)['url']
