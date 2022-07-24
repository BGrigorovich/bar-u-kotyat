from aws_cdk import (
    # Duration,
    Stack,
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    aws_dynamodb as dynamodb, Duration
)

from constructs import Construct


class BarUKotyatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cocktails_table_name = 'Cocktails'

        with open('bar_u_kotyat/update-menu.py', encoding='utf8') as fp:
            handler_code = fp.read()

        lambda_fn = lambda_.Function(
            self,
            'RandomWriter',
            code=lambda_.InlineCode(handler_code),
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
            # TODO: set RCU
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST)
        # todo: enable streams
        # dynamodb_cocktails_table.grant_stream_read(lambda_fn)
        dynamodb_cocktails_table.grant_read_data(lambda_fn)
