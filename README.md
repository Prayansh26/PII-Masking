# FETCH REWARDS - Assessment 

## Thought Process

1. How will you read messages from the queue?
I've utilized the boto3 library to interact with the local SQS service.

2. What type of data structures should be used?
JSON for the message format. Python dictionaries and tuples for intermediate data handling.

3. How will you mask the PII data so that duplicate values can be identified?
I've used SHA-256 hashing with base64 encoding which ensures that sensitive information is hidden and duplicates can be.

4. What will be your strategy for connecting and writing to Postgres?
I've used psycopg2 for both, connecting to the database and then writing into it.

5. Where and how will your application run?
The script runs locally and can be scheduled using cron jobs or task schedulers in a production environment.

## Questions


Deployment and Scalability
Production Deployment

Deploy using container orchestration tools like Kubernetes for scalability.
Use AWS managed services (SQS, RDS) for higher reliability and maintenance.
Additional Components

Implement logging and monitoring (e.g., using AWS CloudWatch, ELK stack).
Set up automated tests and CI/CD pipelines for continuous integration and deployment.
Scaling with Growing Dataset

Use message batching and parallel processing to handle large volumes of data.
Optimize database writes using bulk inserts and indexing.
PII Recovery

Store a mapping of hashed values to original values in a secure, access-controlled environment if recovery is necessary.
Assumptions

The input data schema is consistent.
The database schema is pre-created and matches the expected format.
Next Steps
Implement error handling and retries for robustness.
Add unit tests for the script.
Document the code and process more thoroughly.
Consider implementing a more sophisticated masking mechanism if required.
Conclusion
This project demonstrates an ETL process that reads from an SQS queue, masks PII data, and writes to a Postgres database. The use of Docker ensures that the entire setup can be run locally and is easily portable.