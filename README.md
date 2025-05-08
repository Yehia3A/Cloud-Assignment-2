# Assignment 2: Event-Driven Order Notification System

## Overview
This project builds an event-driven system using AWS services to process order notifications. An SNS topic (`OrderTopic`) publishes order messages, which are received by an SQS queue (`OrderQueue`). A Lambda function (`OrderProcessor`) processes the messages and stores them in a DynamoDB table (`Orders`). A dead-letter queue (`OrderQueueDLQ`) captures failed messages for debugging.

## Setup Instructions
Follow these steps to set up the system in AWS (region: `us-east-1`):

1. **Create an SNS Topic**:
   - Go to the SNS console.
   - Create a Standard topic named `OrderTopic`.
   - Note the ARN: `arn:aws:sns:us-east-1:390402579749:OrderTopic`.

2. **Create SQS Queues**:
   - Go to the SQS console.
   - Create a Standard queue named `OrderQueue` (URL: `https://sqs.us-east-1.amazonaws.com/390402579749:OrderQueue`).
   - Create a Standard queue named `OrderQueueDLQ` for failed messages.
   - Configure `OrderQueue` to use `OrderQueueDLQ` as its dead-letter queue with `maxReceiveCount = 3`.

3. **Subscribe SQS to SNS**:
   - In the SNS console, select `OrderTopic`.
   - Create a subscription with the protocol `SQS` and endpoint `OrderQueue` ARN.
   - Ensure raw message delivery is disabled (messages will be wrapped in an SNS notification).

4. **Create a DynamoDB Table**:
   - Go to the DynamoDB console.
   - Create a table named `Orders` with `orderId` (String) as the partition key.

5. **Create a Lambda Function**:
   - Go to the Lambda console.
   - Create a function named `OrderProcessor` with Python 3.9 runtime.
   - Add the provided `lambda_function.py` code.
   - Set the environment variable `ORDERS_TABLE_NAME` to `Orders`.
   - Add an SQS trigger from `OrderQueue` (batch size: 10).

6. **Configure IAM Permissions**:
   - Attach policies to the Lambda execution role for:
     - SQS: `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on `OrderQueue`.
     - DynamoDB: `dynamodb:PutItem` on `Orders`.
     - CloudWatch Logs: `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`.
   - Update the SQS queue policy to allow SNS to send messages.

## Architecture Diagram
![Architecture Diagram](architecture_diagram.png)

## Testing Steps
1. **Publish a Test Message to SNS**:
   - Go to the SNS console, select `OrderTopic`.
   - Click **Publish message**.
   - Use this test message:
     ```json
     {
         "orderId": "01234",
         "userId": "U123",
         "itemName": "Laptop",
         "quantity": 1,
         "status": "new",
         "timestamp": "2025-05-03T12:00:00Z"
     }
     ```
   - Click **Publish message**.

2. **Capture SQS Message**:
   - Disable the SQS trigger:
     - Go to the Lambda console, select `OrderProcessor`.
     - In **Configuration** > **Triggers**, click the SQS trigger.
     - Edit the event source mapping (UUID: `159fe2d1-f529-4511-9ded-24049d90f621`) and set **Enabled** to "No".
   - Republish the test message using the JSON above.
   - Go to the SQS console, select `OrderQueue`.
   - Click **Send and receive messages** > **Poll for messages**.
   - Take a screenshot of the message.

3. **Process the Message**:
   - Re-enable the SQS trigger (set **Enabled** to "Yes").
   - Republish the test message using the JSON above.
   - Check CloudWatch Logs for `OrderProcessor` (e.g., via the Lambda console under **Monitor** > **View logs in CloudWatch**) for:
     ```
     INFO Processing order: 01234, User: U123, Item: Laptop
     INFO Order 01234 saved to DynamoDB
     ```

4. **Verify DynamoDB**:
   - Go to the DynamoDB console, select `Orders`.
   - Click **Explore table items**.
   - Verify the item matches the test message:
     ```json
     {
         "orderId": "01234",
         "userId": "U123",
         "itemName": "Laptop",
         "quantity": 1,
         "status": "new",
         "timestamp": "2025-05-03T12:00:00Z"
     }
     ```
   - Take a screenshot.

5. **Check Dead-Letter Queue (Optional)**:
   - If processing fails, go to the SQS console, select `OrderQueueDLQ`.
   - Click **Send and receive messages** > **Poll for messages** to debug.

## Bonus: Exported CloudFormation Template
Included is a CloudFormation template (`CF-Order-System.yaml`) that codifies the entire infrastructure, including SNS, SQS, Lambda, and DynamoDB resources. Deploy this template to recreate the system:
- Upload `CF-Order-System.yaml` to the CloudFormation console.
- Create a stack with the name `OrderSystemStack`.
- Verify the resources in the AWS Console after deployment.
