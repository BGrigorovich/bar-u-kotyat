from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb, Duration,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_lambda_event_sources as lambda_event_sources
)

from constructs import Construct


class BarUKotyatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cocktails_table_name = 'Cocktails'

        with open('bar_u_kotyat/update-menu.py', encoding='utf8') as lambda_source:
            lambda_fn = lambda_.Function(
                self,
                'RenderMenu',
                code=lambda_.InlineCode(lambda_source.read()),
                handler='index.main',
                timeout=Duration.seconds(10),
                runtime=lambda_.Runtime.PYTHON_3_9,
                environment={'TABLE_NAME': cocktails_table_name},
            )

        dynamodb_cocktails_table = dynamodb.Table(
            self,
            cocktails_table_name,
            table_name=cocktails_table_name,
            partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING),
            stream=dynamodb.StreamViewType.KEYS_ONLY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )
        dynamodb_cocktails_table.grant_stream_read(lambda_fn)
        dynamodb_cocktails_table.grant_read_data(lambda_fn)

        lambda_fn.add_event_source(
            lambda_event_sources.DynamoEventSource(
                table=dynamodb_cocktails_table,
                starting_position=lambda_.StartingPosition.LATEST,
                enabled=True
            )
        )

        bucket = s3.Bucket(
            self,
            'BarUKotyat',
            versioned=True,
            public_read_access=True,
            website_index_document='menu.html'
        )
        bucket.grant_read_write(lambda_fn)

        with open('bar_u_kotyat/menu_template.html', encoding='utf8') as menu_template:
            s3_deployment.BucketDeployment(
                self,
                'Deploy menu_template.html',
                destination_bucket=bucket,
                sources=[s3_deployment.Source.data('menu_template.html', menu_template.read())]
            )
