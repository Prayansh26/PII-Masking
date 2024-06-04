import psycopg2
import hashlib
import base64
import json
import boto3
import os

# Environment variables for configuration
queue_url = 'http://localstack:4566/000000000000/login-queue'
DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-west-2')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'dummy')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'dummy')

def connect_to_postgres():
    """Connect to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    return conn, cur

def get_sqs_messages():
    """Get messages from local SQS queue using boto3."""
    sqs = boto3.client(
        'sqs',
        use_ssl=False,
        region_name=AWS_REGION_NAME,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        endpoint_url='http://localstack:4566'
    )
    
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5
        )
        return response.get('Messages', [])
    except boto3.exceptions.EndpointConnectionError as e:
        print(f"Error connecting to SQS endpoint: {e}")
        return []

def mask_pii(value):
    """Mask PII values using SHA-256."""
    hasher = hashlib.sha256()
    hasher.update(value.encode('utf-8'))
    return base64.urlsafe_b64encode(hasher.digest()).decode('utf-8')

def process_message(message):
    """Process and mask the PII fields in the message."""
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

def write_to_postgres(records):
    """Write the processed records to the PostgreSQL database."""
    conn, cur = connect_to_postgres()
    insert_query = """
    INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for record in records:
        cur.execute(insert_query, record)
    
    conn.commit()
    cur.close()
    conn.close()

def main():
    """Main function to run the ETL process."""
    messages = get_sqs_messages()

    if not messages:
        print("No messages found in the queue.")
        return

    records = [process_message(msg) for msg in messages]
    write_to_postgres(records)
    print("ETL process completed.")

if __name__ == "__main__":
    print("Starting ETL process...")
    print(f"Queue URL: {queue_url}")
    print("Connecting to SQS and PostgreSQL...")
    main()
