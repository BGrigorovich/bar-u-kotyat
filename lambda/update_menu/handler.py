import os
from dataclasses import dataclass, field
from math import inf
from typing import List

import boto3
from dynamodb_json import json_util as dynamodb_json
from jinja2 import Environment, select_autoescape


s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
table_name = os.getenv('TABLE_NAME')
bucket_name = os.getenv('BUCKET_NAME')

jinja_env = Environment(autoescape=select_autoescape())


@dataclass
class Cocktail:
    name: str
    ingredients: List[str]
    order: int = inf
    available: bool = True
    notes: str = ''

    @property
    def ingredients_str(self):
        return ', '.join(self.ingredients).capitalize()


@dataclass
class CocktailGroup:
    name: str
    order: int = inf
    available: bool = True
    cocktails: List[Cocktail] = field(default_factory=lambda: [])


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

    cocktail_groups = []
    for cocktail in cocktails:
        cocktail = dynamodb_json.loads(cocktail)

        group_name = cocktail.pop('pk')
        try:
            cocktail_group = next(group for group in cocktail_groups if group.name == group_name)
        except StopIteration:
            cocktail_group = CocktailGroup(name=group_name)
            cocktail_groups.append(cocktail_group)

        if cocktail['sk'].startswith('cocktail#'):
            cocktail['name'] = cocktail.pop('sk').replace('cocktail#', '')
            cocktail_group.cocktails.append(Cocktail(**cocktail))
        else:
            cocktail_group.order = cocktail.get('order', inf)
            cocktail_group.available = cocktail.get('available', True)

    cocktail_groups.sort(key=lambda group: group.order)
    for cocktail_group in cocktail_groups:
        cocktail_group.cocktails.sort(key=lambda c: c.order)
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
