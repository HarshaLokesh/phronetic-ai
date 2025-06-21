# Personal Finance Management API

A comprehensive RESTful API for personal finance management with authentication, transaction tracking, budget management, and analytics. Built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- 🔐 **Authentication & Authorization**: JWT-based authentication with secure password hashing
- 💰 **Transaction Management**: Full CRUD operations for financial transactions
- 📊 **Budget Management**: Create and track budgets with progress monitoring
- 📈 **Analytics & Reporting**: Category breakdown, spending analysis, and data transformation
- 🌍 **External API Integration**: Currency conversion and financial data
- 📝 **Comprehensive Logging**: Request/response logging and error tracking
- 🚀 **Production Ready**: Docker support, health checks, and proper error handling

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user profile
- `GET /api/v1/auth/preferences` - Get user preferences
- `PUT /api/v1/auth/preferences` - Update user preferences

### Transactions
- `POST /api/v1/transactions/` - Create a new transaction
- `GET /api/v1/transactions/` - Get user transactions (with filtering)
- `GET /api/v1/transactions/{id}` - Get specific transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/summary/period` - Get transaction summary

### Analytics
- `GET /api/v1/analytics/currency/convert` - Convert currency
- `GET /api/v1/analytics/transactions/category-breakdown` - Category analysis
- `GET /api/v1/analytics/budgets/progress` - Budget progress tracking
- `POST /api/v1/analytics/data/transform` - Data transformation

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend_service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb finance_db
   
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://username:password@localhost/finance_db
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t finance-api .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Application
APP_NAME=Personal Finance API
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost/finance_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
CURRENCY_API_URL=https://api.exchangerate-api.com/v4/latest

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## API Usage Examples

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### 2. Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

### 3. Create a Transaction
```bash
curl -X POST "http://localhost:8000/api/v1/transactions/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "description": "Grocery shopping",
    "category": "Food",
    "transaction_type": "expense"
  }'
```

### 4. Get Transaction Summary
```bash
curl -X GET "http://localhost:8000/api/v1/transactions/summary/period?period=month" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Convert Currency
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/currency/convert?amount=100&from_currency=USD&to_currency=EUR" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### Transactions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `amount`: Transaction amount
- `currency`: Currency code (default: USD)
- `description`: Transaction description
- `category`: Transaction category
- `transaction_type`: income/expense/transfer
- `date`: Transaction date
- `created_at`, `updated_at`: Timestamps

### Budgets Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `name`: Budget name
- `amount`: Budget amount
- `currency`: Currency code
- `period`: daily/weekly/monthly/yearly
- `category`: Budget category
- `start_date`, `end_date`: Budget period
- `is_active`: Budget status
- `created_at`, `updated_at`: Timestamps

### User Preferences Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `default_currency`: Preferred currency
- `timezone`: User timezone
- `notification_enabled`: Notification settings
- `theme`: UI theme preference
- `language`: Language preference
- `created_at`, `updated_at`: Timestamps

## Error Handling

The API returns consistent error responses:

```json
{
  "error": "HTTP 400",
  "detail": "Username already registered"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

## Logging

The application uses structured logging with:
- Console output with colorized formatting
- File rotation (10MB files, 30 days retention)
- Request/response logging
- Error tracking with stack traces

Log files are stored in the `logs/` directory.

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Deployment

### Production Considerations

1. **Security**
   - Change default secret key
   - Use HTTPS
   - Configure CORS properly
   - Set up rate limiting

2. **Database**
   - Use connection pooling
   - Set up database backups
   - Configure proper indexes

3. **Monitoring**
   - Set up health checks
   - Configure logging aggregation
   - Monitor performance metrics

### Cloud Deployment

#### Heroku
```bash
# Create Heroku app
heroku create your-finance-api

# Set environment variables
heroku config:set DATABASE_URL=your_postgres_url
heroku config:set SECRET_KEY=your_secret_key

# Deploy
git push heroku main
```

#### Docker Cloud
```bash
# Build and push to registry
docker build -t your-registry/finance-api .
docker push your-registry/finance-api

# Deploy to cloud platform
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information
