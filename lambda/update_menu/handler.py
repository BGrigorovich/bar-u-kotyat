import boto3
from jinja2 import Environment, PackageLoader, select_autoescape


s3 = boto3.client('s3')

dynamodb = boto3.client('dynamodb')

jinja_env = Environment(autoescape=select_autoescape())
bucket_name = 'bar-u-kotyat'


def lambda_handler(event, context):
    html_context = {

    }

    html_template_string = s3.get_object(
        Bucker=bucket_name, Key='menu_template.html'
    )['Body'].read().decode('utf-8')
    rendered_template = jinja_env.from_string(html_template_string).render(**html_context)

    s3.put_object(Body=rendered_template.encode(), Bucket=bucket_name, Key='menu.html')
    return {
        'message': 'ok'
    }
