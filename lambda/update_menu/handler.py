import boto3
from jinja2 import Environment, PackageLoader, select_autoescape


s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

jinja_env = Environment(
    loader=PackageLoader(),
    autoescape=select_autoescape()
)


def lambda_handler(event, context):
    html_context = {

    }
    jinja_env.from_string().render(**context)
    return { 
        'message' : message
    }
