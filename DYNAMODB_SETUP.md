# DynamoDB Setup Guide

This guide explains how to set up and use DynamoDB with the Training Tracker application.

## Table of Contents
- [Overview](#overview)
- [Single Table Design](#single-table-design)
- [Local Development](#local-development)
- [AWS Production Setup](#aws-production-setup)
- [Environment Variables](#environment-variables)
- [Migration from In-Memory](#migration-from-in-memory)

---

## Overview

The Training Tracker now uses **DynamoDB with Single Table Design** for persistent storage of athletes and training sessions.

### Why Single Table Design?

- **Lower Cost**: One table = one set of provisioned capacity
- **Better Performance**: Related data stored together
- **Efficient Access Patterns**: All queries use primary key or GSI
- **Scalability**: DynamoDB handles scaling automatically

---

## Single Table Design

### Table Structure

**Primary Keys:**
- `PK` (Partition Key): Groups related items
- `SK` (Sort Key): Provides ordering and uniqueness

**Global Secondary Index (GSI1):**
- `GSI1PK` (Partition Key): Enables alternate access patterns
- `GSI1SK` (Sort Key): Provides sorting for queries

### Data Model

#### Athletes
```
PK: ATHLETE#<athlete_id>
SK: ATHLETE#<athlete_id>
Type: ATHLETE
AthleteId: <athlete_id>
Name: <athlete_name>
```

#### Training Sessions
```
PK: ATHLETE#<athlete_id>
SK: SESSION#<session_id>
GSI1PK: SESSION
GSI1SK: <date>#<session_id>
Type: SESSION
SessionId: <session_id>
AthleteId: <athlete_id>
AthleteName: <athlete_name>
Date: <ISO date>
Duration: <float as string>
Distance: <float as string>
Notes: <text>
CreatedAt: <ISO datetime>
UpdatedAt: <ISO datetime>
```

### Access Patterns

| Pattern | Method | Details |
|---------|--------|---------|
| Get all athletes | Scan | Filter: `Type='ATHLETE'` |
| Get athlete by ID | GetItem | `PK='ATHLETE#<id>', SK='ATHLETE#<id>'` |
| Get athlete's sessions | Query | `PK='ATHLETE#<id>', SK begins_with 'SESSION#'` |
| Get all sessions | Query GSI1 | `GSI1PK='SESSION'` |
| Get session by ID | Query GSI1 | `GSI1PK='SESSION'` + Filter: `SessionId='<id>'` |

---

## Local Development

### Prerequisites

1. Install DynamoDB Local (Docker recommended)
2. Install boto3: `./pw install`

### Option 1: Docker (Recommended)

```bash
# Start DynamoDB Local
docker run -d -p 8000:8000 \
  --name dynamodb-local \
  amazon/dynamodb-local

# Verify it's running
curl http://localhost:8000

# Stop when done
docker stop dynamodb-local

# Remove container
docker rm dynamodb-local
```

### Option 2: Download JAR

```bash
# Download DynamoDB Local
wget https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz

# Extract
tar -xzf dynamodb_local_latest.tar.gz

# Run
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

# Runs on http://localhost:8000
```

### Create the Table

```bash
# Set environment variables for local development
export DYNAMODB_ENDPOINT=http://localhost:8000
export DYNAMODB_TABLE_NAME=training-tracker
export AWS_REGION=us-east-1

# Create the table
python scripts/create_dynamodb_table.py
```

### Run the Application

```bash
# Set environment variables
export DYNAMODB_ENDPOINT=http://localhost:8000
export DYNAMODB_TABLE_NAME=training-tracker
export AWS_REGION=us-east-1

# Start the application
./pw start
```

### Access the Application

- API: http://localhost:8080
- UI: Open `training-tracker-ui/dist/index.html` in a browser

---

## AWS Production Setup

### 1. Create IAM Policy

Create a policy with DynamoDB permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/training-tracker",
        "arn:aws:dynamodb:*:*:table/training-tracker/index/*"
      ]
    }
  ]
}
```

### 2. Create the Table

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_NAME=training-tracker

# Create table (no DYNAMODB_ENDPOINT for AWS)
python scripts/create_dynamodb_table.py
```

### 3. Deploy Application

Configure your application with:

```bash
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_NAME=training-tracker
# Don't set DYNAMODB_ENDPOINT for production
```

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DYNAMODB_TABLE_NAME` | Name of the DynamoDB table | `training-tracker` |
| `AWS_REGION` | AWS region | `us-east-1` |

### Optional

| Variable | Description | When to Use |
|----------|-------------|-------------|
| `DYNAMODB_ENDPOINT` | DynamoDB endpoint URL | Local development only |
| `AWS_ACCESS_KEY_ID` | AWS access key | If not using IAM roles |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | If not using IAM roles |

### Configuration Examples

**Local Development:**
```bash
export DYNAMODB_ENDPOINT=http://localhost:8000
export DYNAMODB_TABLE_NAME=training-tracker
export AWS_REGION=us-east-1
```

**AWS EC2/ECS/Lambda (with IAM role):**
```bash
export DYNAMODB_TABLE_NAME=training-tracker
export AWS_REGION=us-east-1
# IAM role provides credentials automatically
```

**AWS with Access Keys:**
```bash
export DYNAMODB_TABLE_NAME=training-tracker
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

## Migration from In-Memory

The application previously used in-memory storage. Here's how the migration was done:

### What Changed

1. **Dependencies**: Added `boto3` to `pyproject.toml`
2. **Storage Layer**: Rewrote `storage.py` to use DynamoDB
3. **API Functions**: No changes needed (same interface)
4. **Frontend**: No changes needed

### Code Changes

**Before (In-Memory):**
```python
athletes_db: Dict[str, Athlete] = {}
training_sessions_db: Dict[str, TrainingSession] = {}

def get_athlete(athlete_id: str) -> Athlete | None:
    return athletes_db.get(athlete_id)
```

**After (DynamoDB):**
```python
def get_athlete(athlete_id: str) -> Athlete | None:
    table = _get_table()
    response = table.get_item(
        Key={
            'PK': f'ATHLETE#{athlete_id}',
            'SK': f'ATHLETE#{athlete_id}'
        }
    )
    item = response.get('Item')
    return _item_to_athlete(item) if item else None
```

### Benefits

| Feature | In-Memory | DynamoDB |
|---------|-----------|----------|
| Data Persistence | ❌ Lost on restart | ✅ Permanent |
| Scalability | ❌ Limited by RAM | ✅ Unlimited |
| Cost | Free | Pay per use |
| Development | Simple | Requires setup |
| Production Ready | ❌ No | ✅ Yes |

---

## Testing

### Run Tests with Mock

Tests use mocked DynamoDB (no real AWS connection needed):

```bash
./pw test
```

### Run Tests with Local DynamoDB

```bash
# Start DynamoDB Local
docker run -d -p 8000:8000 amazon/dynamodb-local

# Set environment
export DYNAMODB_ENDPOINT=http://localhost:8000
export DYNAMODB_TABLE_NAME=training-tracker-test

# Create test table
python scripts/create_dynamodb_table.py

# Run tests
./pw test
```

---

## Troubleshooting

### Error: "Unable to locate credentials"

**Solution**: Set AWS credentials or use IAM role

```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Error: "ResourceNotFoundException"

**Solution**: Create the table

```bash
python scripts/create_dynamodb_table.py
```

### Error: "Connection refused" (Local)

**Solution**: Start DynamoDB Local

```bash
docker run -d -p 8000:8000 amazon/dynamodb-local
```

### Error: "ResourceInUseException"

**Solution**: Table already exists (this is OK)

### Slow Queries

**Solution**: Check your access patterns
- Use Query instead of Scan when possible
- Ensure GSI is being used for cross-athlete queries
- Consider adding more GSIs for specific patterns

---

## Best Practices

### 1. Use IAM Roles in Production
Don't hardcode credentials. Use IAM roles for EC2, ECS, Lambda, etc.

### 2. Set Appropriate Capacity
For production:
- Start with on-demand billing
- Switch to provisioned after understanding usage patterns
- Use auto-scaling

### 3. Monitor Costs
- Enable CloudWatch metrics
- Set up billing alerts
- Use AWS Cost Explorer

### 4. Backup Strategy
- Enable point-in-time recovery
- Set up automated backups
- Test restore procedures

### 5. Table Naming
- Use environment-specific table names
- Example: `training-tracker-prod`, `training-tracker-dev`

---

## Cost Estimation

### DynamoDB Pricing (us-east-1)

**On-Demand:**
- Write: $1.25 per million requests
- Read: $0.25 per million requests

**Provisioned (5 RCU, 5 WCU):**
- ~$2.50/month for table
- ~$2.50/month for GSI
- **Total: ~$5/month**

**For typical usage:**
- 100 sessions/day = ~3000 writes/month
- 1000 reads/day = ~30,000 reads/month
- **Estimated cost: $0.04/month** (on-demand)

Start with **on-demand** for development, switch to **provisioned** when traffic is predictable.

---

## Next Steps

1. ✅ Install DynamoDB Local for development
2. ✅ Create the table using the script
3. ✅ Configure environment variables
4. ✅ Test locally
5. ✅ Deploy to AWS when ready
6. ✅ Monitor and optimize

---

## Additional Resources

- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Single Table Design Best Practices](https://aws.amazon.com/blogs/compute/creating-a-single-table-design-with-amazon-dynamodb/)
- [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)
- [Boto3 DynamoDB](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review AWS DynamoDB documentation
3. Check application logs for detailed error messages
4. Verify environment variables are set correctly
