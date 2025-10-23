#!/usr/bin/env python3
"""Script to create DynamoDB table with single table design for Training Tracker."""

import os
import sys

import boto3
from botocore.exceptions import ClientError


def create_table():
    """Create the DynamoDB table with single table design."""

    # Get configuration from environment variables
    table_name = os.environ.get("DYNAMODB_TABLE_NAME", "training-tracker")
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT")  # For local development
    region_name = os.environ.get("AWS_REGION", "us-east-1")

    # Create DynamoDB client
    dynamodb = boto3.client(
        "dynamodb",
        endpoint_url=endpoint_url,
        region_name=region_name,
    )

    print(f"Creating DynamoDB table: {table_name}")
    if endpoint_url:
        print(f"Using local endpoint: {endpoint_url}")

    try:
        # Create table with single table design
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "SK", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {
                        "ProjectionType": "ALL",
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5,
                    },
                },
            ],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )

        print(f"✅ Table '{table_name}' created successfully!")
        print(f"Table ARN: {response['TableDescription'].get('TableArn', 'N/A')}")
        print(f"Table Status: {response['TableDescription']['TableStatus']}")

        # Wait for table to be active
        print("\nWaiting for table to be active...")
        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=table_name)
        print("✅ Table is now active and ready to use!")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"⚠️  Table '{table_name}' already exists")

            # Describe the table to show its current state
            response = dynamodb.describe_table(TableName=table_name)
            print(f"Table Status: {response['Table']['TableStatus']}")
            print(f"Table ARN: {response['Table']['TableArn']}")
        else:
            print(f"❌ Error creating table: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def print_table_design():
    """Print information about the single table design."""
    print("\n" + "=" * 80)
    print("DynamoDB Single Table Design")
    print("=" * 80)
    print("""
Access Patterns:
1. Get all athletes                   → Scan with filter Type='ATHLETE'
2. Get athlete by ID                  → GetItem PK='ATHLETE#<id>' SK='ATHLETE#<id>'
3. Get all sessions for an athlete    → Query PK='ATHLETE#<id>' SK begins_with 'SESSION#'
4. Get all sessions (all athletes)    → Query GSI1 where GSI1PK='SESSION'
5. Get session by ID                  → Query GSI1 with filter SessionId='<id>'

Table Structure:
┌──────────────────────┬──────────────────────┬────────┬──────────────────────┐
│ PK                   │ SK                   │ Type   │ Other Attributes     │
├──────────────────────┼──────────────────────┼────────┼──────────────────────┤
│ ATHLETE#athlete-1    │ ATHLETE#athlete-1    │ ATHLETE│ AthleteId, Name      │
│ ATHLETE#athlete-1    │ SESSION#session-1    │ SESSION│ SessionId, Date, ... │
│ ATHLETE#athlete-1    │ SESSION#session-2    │ SESSION│ SessionId, Date, ... │
│ ATHLETE#athlete-2    │ ATHLETE#athlete-2    │ ATHLETE│ AthleteId, Name      │
│ ATHLETE#athlete-2    │ SESSION#session-3    │ SESSION│ SessionId, Date, ... │
└──────────────────────┴──────────────────────┴────────┴──────────────────────┘

GSI1 (Global Secondary Index):
┌──────────────────────┬──────────────────────┬────────────────────────────┐
│ GSI1PK               │ GSI1SK               │ Purpose                    │
├──────────────────────┼──────────────────────┼────────────────────────────┤
│ SESSION              │ 2025-10-20#session-1 │ Query all sessions sorted  │
│ SESSION              │ 2025-10-21#session-2 │ by date                    │
│ SESSION              │ 2025-10-22#session-3 │                            │
└──────────────────────┴──────────────────────┴────────────────────────────┘

Benefits:
✓ Single table = lower cost
✓ Related data stored together (athlete + their sessions)
✓ Efficient queries for all access patterns
✓ GSI enables querying all sessions across athletes
✓ Sortable by date using GSI1SK
""")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print_table_design()
    create_table()
