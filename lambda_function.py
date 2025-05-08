import json
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ORDERS_TABLE_NAME'])

def lambda_handler(event, context):
    if 'Records' in event:
        for record in event['Records']:
            try:
                message = json.loads(record['body'])
                sns_message = json.loads(message['Message'])
            except (KeyError, json.JSONDecodeError) as e:
                logger.error(f"Error parsing SQS message: {str(e)}")
                raise e
    else:
        sns_message = event

    try:
        order_id = sns_message['orderId']
        user_id = sns_message['userId']
        item_name = sns_message['itemName']
        quantity = sns_message['quantity']
        status = sns_message['status']
        timestamp = sns_message['timestamp']
        
        table.put_item(
            Item={
                'orderId': order_id,
                'userId': user_id,
                'itemName': item_name,
                'quantity': quantity,
                'status': status,
                'timestamp': timestamp
            }
        )
        
        logger.info(f"Processing order: {order_id}, User: {user_id}, Item: {item_name}")
        logger.info(f"Order {order_id} saved to DynamoDB")
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed messages')
    }