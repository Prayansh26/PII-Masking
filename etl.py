import boto3
import psycopg2
import hashlib
import base64
import json

# Getting messages
def get_sqs_messages(queue_url):
    """Getting messages from local SQS queue"""

    sqs = boto3.client('sqs', endpoint_url='http://localhost:4566', region_name='us-east-1')
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5
    )
    messages = response.get('Messages', [])
    return messages

# Masking PII values
def mask_pii(value):
    """Masking the PII input values using SHA-256 and handling duplicate values"""

    hasher = hashlib.sha256()
    hasher.update(value.encode('utf-8'))
    return base64.urlsafe_b64encode(hasher.digest()).decode('utf-8')

# Processing the message
def process_message(message):
    """ - Pasre the JSON message
        - Mask the PII fields
        - Flattens the data for insertion
    """

    body = json.loads(message['Body'])
    masked_device_id = mask_pii(body['device_id'])
    masked_ip = mask_pii(body['ip'])
    
    return (
        body['user_id'],
        body['device_type'],
        masked_ip,
        masked_device_id,
        body['locale'],
        body['app_version'],
        body['create_date']
    )

# Writing data to table
def write_to_postgres(records):
    """  Write the processed records to the Postgres database."""

    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    
    insert_query = """
    INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for record in records:
        cur.execute(insert_query, record)
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # Define the SQS queue URL
    queue_url = 'http://localhost:4566/000000000000/login-queue'

    # Fetch messages from the SQS queue
    messages = get_sqs_messages(queue_url)
    
    if not messages:
        print("No messages found in the queue.")
        exit()
    
    # Process each message
    records = [process_message(msg) for msg in messages]

    # Write data to POstgres Database
    write_to_postgres(records)
    print("ETL process completed.")