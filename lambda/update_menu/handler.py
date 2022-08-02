import os
from collections import defaultdict

import boto3
from jinja2 import Environment, select_autoescape


s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
table_name = os.getenv('TABLE_NAME')
bucket_name = os.getenv('BUCKET_NAME')

jinja_env = Environment(autoescape=select_autoescape())


def lambda_handler(event, context):
    paginator = dynamodb.get_paginator('scan')

    page_iterator = paginator.paginate(
        TableName=table_name,
        FilterExpression='available = :available',
        ExpressionAttributeValues={
            ':available': {'BOOL': True}
        }
    )
    cocktails = []
    for page in page_iterator:
        cocktails.extend(page['Items'])

    cocktail_groups = defaultdict(list)
    for cocktail in cocktails:
        if cocktail['sk']['S'].startswith('cocktail#'):
            group_name = cocktail['pk']['S']
            ingredients = [ing['S'] for ing in cocktail['ingredients']['L']]
            cocktail_groups[group_name].append({
                'name': cocktail['sk']['S'].split('#')[1],
                'ingredients': ', '.join(ingredients).capitalize()
            })
            cocktail['name'] = cocktail['sk']['S'].split('#')[1]
            cocktail['ingredients'] = ', '.join(ingredients).capitalize()

    html_context = dict(
        cocktail_groups=cocktail_groups,
    )

    html_template_string = s3.get_object(
        Bucket=bucket_name, Key='menu_template.html'
    )['Body'].read().decode('utf-8')
    rendered_template = jinja_env.from_string(html_template_string).render(**html_context)

    s3.put_object(Body=rendered_template.encode(), Bucket=bucket_name, Key='menu.html', ContentType='text/html')
    return {
        'message': 'ok'
    }
