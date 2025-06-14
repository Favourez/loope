# Emergency Response App - API Documentation

## Base URL
```
http://127.0.0.1:3000/api/v1
```

## Authentication
Most endpoints require an API key. Include it in the request header:
```
X-API-Key: emergency-api-key-2024
```

Or as a query parameter:
```
?api_key=emergency-api-key-2024
```

## Response Format
All API responses follow this format:
```json
{
  "status": "success|error",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    // Response data here
  }
}
```

## Endpoints

### Authentication

#### POST /auth/login
Login with username/email and password.

**Request Body:**
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "message": "Login successful",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "user@test.com",
      "full_name": "Test User",
      "user_type": "regular"
    },
    "token": "token_1_1704110400.0"
  }
}
```

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "new@test.com",
  "password": "password123",
  "full_name": "New User",
  "phone": "+237123456789",
  "user_type": "regular"
}
```

### Emergency Reports

#### GET /emergencies
Get all emergency reports with optional filtering.

**Query Parameters:**
- `status`: Filter by status (pending, in_progress, resolved, cancelled)
- `severity`: Filter by severity (low, medium, high, critical)
- `limit`: Limit number of results

**Example:**
```
GET /api/v1/emergencies?status=pending&limit=10
```

#### POST /emergencies
Create a new emergency report.

**Request Body:**
```json
{
  "emergency_type": "fire",
  "location": "Downtown Yaoundé",
  "description": "Building fire on main street",
  "severity": "high",
  "latitude": 3.8634,
  "longitude": 11.5167,
  "user_id": 1
}
```

#### GET /emergencies/{id}
Get specific emergency report by ID.

#### PUT /emergencies/{id}/status
Update emergency report status.

**Request Body:**
```json
{
  "status": "in_progress"
}
```

### Fire Departments

#### GET /fire-departments
Get all fire departments.

**Response:**
```json
{
  "status": "success",
  "data": {
    "fire_departments": [
      {
        "id": 1,
        "department_name": "Yaoundé Central Fire Department",
        "department_location": "Yaoundé, Centre Region",
        "phone": "+237118001"
      }
    ],
    "total_count": 1
  }
}
```

### Messages

#### GET /messages
Get community messages.

**Query Parameters:**
- `limit`: Number of messages to return (default: 50)

#### POST /messages
Create a new community message.

**Request Body:**
```json
{
  "content": "Emergency update: Road blocked on Avenue Kennedy",
  "message_type": "alert",
  "user_id": 1
}
```

#### DELETE /messages/{id}
Delete a message.

**Query Parameters:**
- `user_id`: ID of user requesting deletion

### First Aid

#### GET /first-aid
Get all first aid practices with optional filtering.

**Query Parameters:**
- `category`: Filter by emergency type
- `difficulty`: Filter by difficulty level

**Response:**
```json
{
  "status": "success",
  "data": {
    "first_aid_practices": [
      {
        "id": 1,
        "title": "CPR (Cardiopulmonary Resuscitation)",
        "description": "Life-saving technique for cardiac arrest",
        "emergency_type": "Cardiac Emergency",
        "difficulty": "Intermediate",
        "duration": "5-10 minutes",
        "image": "https://images.unsplash.com/...",
        "video_url": "https://www.youtube.com/embed/...",
        "keywords": ["cardiac arrest", "heart attack", "unconscious"]
      }
    ],
    "total_count": 10
  }
}
```

#### GET /first-aid/{id}
Get specific first aid practice by ID.

### System

#### GET /health
Health check endpoint (no API key required).

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "service": "Emergency Response API"
  }
}
```

#### GET /status
System status with detailed information.

**Response:**
```json
{
  "status": "success",
  "data": {
    "system_status": "operational",
    "statistics": {
      "total_emergency_reports": 25,
      "pending_emergencies": 3,
      "total_messages": 150,
      "total_fire_departments": 18,
      "total_first_aid_practices": 10
    },
    "uptime": "Available",
    "last_updated": "2024-01-01T12:00:00.000Z"
  }
}
```

## Error Codes

- `400` - Bad Request (missing required fields, invalid data)
- `401` - Unauthorized (invalid or missing API key)
- `404` - Not Found (resource doesn't exist)
- `405` - Method Not Allowed
- `500` - Internal Server Error

## Example Usage with curl

### Get all emergencies
```bash
curl -H "X-API-Key: emergency-api-key-2024" \
     http://127.0.0.1:3000/api/v1/emergencies
```

### Create emergency report
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "X-API-Key: emergency-api-key-2024" \
     -d '{"emergency_type":"fire","location":"Test Location","description":"Test emergency","severity":"high"}' \
     http://127.0.0.1:3000/api/v1/emergencies
```

### Login
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"password123"}' \
     http://127.0.0.1:3000/api/v1/auth/login
```

## Testing with Postman

1. Import the API endpoints into Postman
2. Set up environment variables:
   - `base_url`: http://127.0.0.1:3000/api/v1
   - `api_key`: emergency-api-key-2024
3. Test each endpoint with sample data
4. Verify response formats and error handling
