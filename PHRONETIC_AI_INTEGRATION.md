# Phronetic AI Integration Guide

This document provides comprehensive instructions for integrating the Personal Finance Management API with Phronetic AI agents.

## Overview

The Personal Finance API provides three main categories of tools for Phronetic AI agents:

1. **Authentication & User Management** - User registration, login, and preferences
2. **Transaction Management** - CRUD operations for financial transactions
3. **Analytics & Data Transformation** - Currency conversion, data analysis, and transformation

## Tool Definitions for Phronetic AI

### 1. Authentication Tools

#### Register User
```json
{
  "name": "register_user",
  "description": "Register a new user account for the finance management system",
  "parameters": {
    "type": "object",
    "properties": {
      "username": {
        "type": "string",
        "description": "Unique username for the account"
      },
      "email": {
        "type": "string",
        "description": "Valid email address"
      },
      "password": {
        "type": "string",
        "description": "Secure password (minimum 8 characters)"
      },
      "full_name": {
        "type": "string",
        "description": "User's full name"
      }
    },
    "required": ["username", "email", "password"]
  }
}
```

#### Login User
```json
{
  "name": "login_user",
  "description": "Authenticate user and get access token",
  "parameters": {
    "type": "object",
    "properties": {
      "username": {
        "type": "string",
        "description": "Username for authentication"
      },
      "password": {
        "type": "string",
        "description": "User password"
      }
    },
    "required": ["username", "password"]
  }
}
```

### 2. Transaction Management Tools

#### Create Transaction
```json
{
  "name": "create_transaction",
  "description": "Create a new financial transaction",
  "parameters": {
    "type": "object",
    "properties": {
      "amount": {
        "type": "number",
        "description": "Transaction amount (positive number)"
      },
      "description": {
        "type": "string",
        "description": "Transaction description"
      },
      "category": {
        "type": "string",
        "description": "Transaction category (e.g., Food, Transportation, Entertainment)"
      },
      "transaction_type": {
        "type": "string",
        "enum": ["income", "expense", "transfer"],
        "description": "Type of transaction"
      },
      "currency": {
        "type": "string",
        "description": "Currency code (default: USD)"
      },
      "date": {
        "type": "string",
        "format": "date-time",
        "description": "Transaction date (ISO format)"
      }
    },
    "required": ["amount", "description", "transaction_type"]
  }
}
```

#### Get Transactions
```json
{
  "name": "get_transactions",
  "description": "Retrieve user transactions with optional filtering",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "Maximum number of transactions to return (default: 100)"
      },
      "transaction_type": {
        "type": "string",
        "enum": ["income", "expense", "transfer"],
        "description": "Filter by transaction type"
      },
      "category": {
        "type": "string",
        "description": "Filter by category"
      },
      "start_date": {
        "type": "string",
        "format": "date-time",
        "description": "Filter transactions from this date"
      },
      "end_date": {
        "type": "string",
        "format": "date-time",
        "description": "Filter transactions until this date"
      }
    }
  }
}
```

#### Get Transaction Summary
```json
{
  "name": "get_transaction_summary",
  "description": "Get summary of transactions for a specific period",
  "parameters": {
    "type": "object",
    "properties": {
      "period": {
        "type": "string",
        "enum": ["day", "week", "month", "year"],
        "description": "Time period for summary (default: month)"
      }
    }
  }
}
```

### 3. Analytics & Data Transformation Tools

#### Convert Currency
```json
{
  "name": "convert_currency",
  "description": "Convert amount between different currencies using real-time exchange rates",
  "parameters": {
    "type": "object",
    "properties": {
      "amount": {
        "type": "number",
        "description": "Amount to convert (positive number)"
      },
      "from_currency": {
        "type": "string",
        "description": "Source currency code (3 letters, e.g., USD)"
      },
      "to_currency": {
        "type": "string",
        "description": "Target currency code (3 letters, e.g., EUR)"
      }
    },
    "required": ["amount", "from_currency", "to_currency"]
  }
}
```

#### Transform Financial Data
```json
{
  "name": "transform_financial_data",
  "description": "Transform financial data using various algorithms",
  "parameters": {
    "type": "object",
    "properties": {
      "data": {
        "type": "object",
        "description": "Financial data to transform (must include 'transactions' array)"
      },
      "transformation_type": {
        "type": "string",
        "enum": ["summarize", "categorize", "normalize", "aggregate"],
        "description": "Type of transformation to apply"
      }
    },
    "required": ["data", "transformation_type"]
  }
}
```

## API Base URL Configuration

Set the base URL for all API calls:
```
https://your-api-domain.com/api/v1
```

For local development:
```
http://localhost:8000/api/v1
```

## Authentication Flow

1. **Register User**: Create a new user account
2. **Login**: Get access token for authenticated requests
3. **Use Token**: Include token in Authorization header for all subsequent requests

### Example Authentication Flow

```python
# 1. Register user
register_response = requests.post(
    "https://your-api-domain.com/api/v1/auth/register",
    json={
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securepassword123",
        "full_name": "John Doe"
    }
)

# 2. Login to get token
login_response = requests.post(
    "https://your-api-domain.com/api/v1/auth/login",
    data={
        "username": "john_doe",
        "password": "securepassword123"
    }
)
token = login_response.json()["access_token"]

# 3. Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
```

## Multi-Step Agent Examples

### Example 1: Personal Finance Assistant

**Agent Goal**: Help users manage their finances by tracking expenses and providing insights.

**Tool Chain**:
1. `register_user` or `login_user` - Authenticate user
2. `create_transaction` - Add new expenses/income
3. `get_transaction_summary` - Get spending overview
4. `convert_currency` - Convert amounts if needed
5. `transform_financial_data` - Analyze spending patterns

**Example Conversation**:
```
User: "I spent $50 on groceries today"
Agent: 
1. Creates transaction: amount=50, category="Food", type="expense"
2. Gets monthly summary to show current spending
3. Analyzes food spending patterns
4. Provides insights: "You've spent $200 on food this month, which is 20% of your total expenses"
```

### Example 2: Budget Planning Agent

**Agent Goal**: Help users create and track budgets.

**Tool Chain**:
1. `login_user` - Authenticate user
2. `get_transactions` - Get recent transactions
3. `transform_financial_data` - Categorize spending
4. `convert_currency` - Handle multi-currency budgets
5. `get_transaction_summary` - Track budget progress

**Example Conversation**:
```
User: "I want to set a $500 monthly budget for entertainment"
Agent:
1. Gets current entertainment spending
2. Analyzes spending patterns
3. Creates budget recommendations
4. Sets up tracking for the new budget
```

### Example 3: Financial Analysis Agent

**Agent Goal**: Provide detailed financial analysis and recommendations.

**Tool Chain**:
1. `login_user` - Authenticate user
2. `get_transactions` - Get comprehensive transaction history
3. `transform_financial_data` - Multiple transformations (summarize, categorize, aggregate)
4. `convert_currency` - Normalize multi-currency data
5. `get_transaction_summary` - Compare different time periods

**Example Conversation**:
```
User: "Analyze my spending patterns and give me recommendations"
Agent:
1. Retrieves all transactions
2. Performs data transformation (categorize, aggregate by month)
3. Identifies spending trends
4. Provides personalized recommendations
5. Suggests budget adjustments
```

## Error Handling

The API returns consistent error responses that agents should handle:

```json
{
  "error": "HTTP 400",
  "detail": "Username already registered"
}
```

**Common Error Scenarios**:
- `401 Unauthorized`: Invalid or expired token
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server-side error

**Agent Error Handling Strategy**:
1. Check response status code
2. Parse error message
3. Provide user-friendly error explanation
4. Suggest corrective actions
5. Retry with corrected parameters if appropriate

## Rate Limiting and Best Practices

### Rate Limiting
- API calls are limited to 100 requests per minute per user
- Implement exponential backoff for retries
- Cache frequently accessed data

### Best Practices
1. **Token Management**: Store and reuse tokens efficiently
2. **Batch Operations**: Group related operations when possible
3. **Error Recovery**: Implement graceful error handling
4. **Data Validation**: Validate user input before API calls
5. **Caching**: Cache user preferences and frequently accessed data

## Testing Your Integration

### 1. Test Authentication Flow
```bash
# Test registration
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# Test login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 2. Test Transaction Operations
```bash
# Create transaction
curl -X POST "http://localhost:8000/api/v1/transactions/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 50, "description": "Grocery shopping", "category": "Food", "transaction_type": "expense"}'

# Get transactions
curl -X GET "http://localhost:8000/api/v1/transactions/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Test Analytics
```bash
# Currency conversion
curl -X GET "http://localhost:8000/api/v1/analytics/currency/convert?amount=100&from_currency=USD&to_currency=EUR" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Data transformation
curl -X POST "http://localhost:8000/api/v1/analytics/data/transform?transformation_type=summarize" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transactions": [{"amount": 100, "type": "income"}, {"amount": 50, "type": "expense"}]}'
```

## Deployment Considerations

### Production Deployment
1. **HTTPS**: Always use HTTPS in production
2. **Environment Variables**: Configure all environment variables
3. **Database**: Use production-grade database (PostgreSQL)
4. **Monitoring**: Set up logging and monitoring
5. **Backup**: Implement regular database backups

### Security
1. **Token Expiration**: Set appropriate token expiration times
2. **Input Validation**: Validate all user inputs
3. **Rate Limiting**: Implement rate limiting
4. **CORS**: Configure CORS properly for your domain

## Support and Troubleshooting

### Common Issues
1. **Authentication Errors**: Check token validity and expiration
2. **Database Connection**: Verify database connectivity
3. **External API Failures**: Handle currency API timeouts gracefully
4. **Data Validation**: Ensure all required fields are provided

### Debugging
1. Check API logs: `docker-compose logs api`
2. Verify database connection
3. Test individual endpoints
4. Check environment variables

### Getting Help
- Review API documentation at `/docs`
- Check application logs
- Test with provided test script
- Create issues in the repository

## Conclusion

This Personal Finance API provides a robust foundation for building intelligent financial management agents on Phronetic AI. The comprehensive set of tools enables agents to handle complex financial workflows while maintaining security and data integrity.

For questions or support, please refer to the main README.md file or create an issue in the repository.

Deliverables:

1. Link to your live agent on the Phronetic AI platform:
   https://meet-agents.rediff.com/x5xwEN9CriV3kdvo/rooms/7mqb-nh87

2. Link to your custom backend service's public endpoint:
   ✅ https://phronetic-ai-personal-finance-prd.up.railway.app

3. Link to the GitHub repository:
   ✅ https://github.com/HarshaLokesh/phronetic-ai

4. Evaluation & improvement report:
   ✅ https://github.com/HarshaLokesh/phronetic-ai/blob/main/EVALUATION_REPORT.md