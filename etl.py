import boto3
import psycopg2
import hashlib
import base64
import json

#Getting messages
def get_sqs_messages(queue_url):
    """Getting messages from local SQS queue"""
    sqs = boto3.client(
        'sqs',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
        region_name='us-east-1',
        endpoint_url='http://localstack:4566'
    )
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5
    )
    return response.get('Messages', [])

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
    """Write the processed records to the Postgres database"""
    conn_str = "dbname=postgres user=postgres password=postgres host=postgres port=5432"
    with psycopg2.connect(conn_str) as conn:
        with conn.cursor() as cur:
            insert_query = """
            INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.executemany(insert_query, records)
            conn.commit()
# def write_to_postgres(records):
#     """  Write the processed records to the Postgres database."""

#     conn = psycopg2.connect(
#         dbname="postgres",
#         user="postgres",
#         password="postgres",
#         host="localhost",
#         port="5432"
#     )
#     cur = conn.cursor()
    
#     insert_query = """
#     INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
#     VALUES (%s, %s, %s, %s, %s, %s, %s)
#     """
#     for record in records:
#         cur.execute(insert_query, record)
    
#     conn.commit()
#     cur.close()
#     conn.close()

if __name__ == "__main__":
    try:
        messages = get_sqs_messages(queue_url)
        if not messages:
            print("No messages found in the queue.")
            exit()
        records = [process_message(msg) for msg in messages]
        write_to_postgres(records)
        print("ETL process completed.")
    except Exception as e:
        print(f"An error occurred: {e}")


    # # Define the SQS queue URL
    # queue_url = 'http://localhost:4566/000000000000/login-queue'

    # # Fetch messages from the SQS queue
    # messages = get_sqs_messages(queue_url)
    
    # if not messages:
    #     print("No messages found in the queue.")
    #     exit()
    
    # # Process each message
    # records = [process_message(msg) for msg in messages]

    # # Write data to POstgres Database
    # write_to_postgres(records)
    # print("ETL process completed.")
