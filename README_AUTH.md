# Emergency Response App - Authentication System

## Overview
This application now includes a complete authentication system with SQLite3 database, dual registration for regular users and fire departments, and separate landing pages based on user type.

## Features

### 🔐 Authentication System
- User registration with choice between regular user and fire department
- Secure login with password hashing (bcrypt)
- Session management with Flask-Login
- Role-based access control

### 🏠 Landing Pages
- **Regular Users**: Access to emergency reporting, first aid guides, and maps
- **Fire Departments**: Emergency response dashboard with active reports, status management, and quick actions

### 🗄️ Database Structure
- **Users Table**: Stores user accounts with type differentiation
- **Emergency Reports Table**: Stores all emergency reports with status tracking
- **User Sessions Table**: Manages user sessions

## Test Accounts

### Regular User Account
- **Username**: `testuser`
- **Password**: `password123`
- **Access**: Regular user landing page with emergency reporting

### Fire Department Accounts
- **Yaoundé Fire Department**
  - **Username**: `yaoundefire`
  - **Password**: `firepass123`
  - **Department**: Yaoundé Central Fire Department

- **Douala Fire Department**
  - **Username**: `doualafire`
  - **Password**: `firepass123`
  - **Department**: Douala Port Fire Department

## How to Use

### 1. Start the Application
```bash
python app.py
```

### 2. Access the Application
Open your browser and go to: `http://127.0.0.1:3000`

### 3. Registration Process
1. Click "Register here" on the login page
2. Choose account type (Regular User or Fire Department)
3. Fill in the required information
4. Submit registration

### 4. Login Process
1. Enter username and password
2. System automatically redirects based on user type:
   - Regular users → Emergency reporting dashboard
   - Fire departments → Emergency response management dashboard

## Fire Department Dashboard Features

### 📊 Dashboard Statistics
- Active emergency reports count
- Reports currently being responded to
- Daily resolved reports count
- Department information

### 🚨 Emergency Reports Management
- View all emergency reports in real-time
- Update report status (Reported → Responding → Resolved)
- View reporter contact information
- Priority-based color coding (Critical, High, Medium, Low)

### ⚡ Quick Actions
- Broadcast alerts (coming soon)
- Request backup (coming soon)
- View emergency map
- Generate reports (coming soon)

### 📞 Emergency Contacts
- Quick access to emergency hotlines
- Police: 117
- Medical: 119
- Fire Command: 118-001

## Database Files
- `emergency_app.db`: Main SQLite database
- `database.py`: Database models and functions
- `auth.py`: Authentication helper functions

## Security Features
- Password hashing with bcrypt
- Session management
- CSRF protection
- Role-based access control
- Input validation

## API Endpoints

### Authentication
- `POST /register`: User registration
- `POST /login`: User login
- `GET /logout`: User logout

### Emergency Management
- `POST /report-emergency`: Submit emergency report (authenticated users)
- `POST /update-report-status`: Update report status (fire departments only)

## File Structure
```
├── app.py                          # Main Flask application
├── database.py                     # Database models and functions
├── auth.py                         # Authentication helpers
├── create_test_data.py            # Script to create test data
├── emergency_app.db               # SQLite database
├── templates/
│   ├── register.html              # Registration page
│   ├── login.html                 # Login page
│   ├── landing.html               # Regular user dashboard
│   ├── fire_department_landing.html # Fire department dashboard
│   └── ...                        # Other templates
└── requirements.txt               # Python dependencies
```

## Next Steps
- Implement real-time notifications
- Add emergency broadcast system
- Implement backup request system
- Add report generation features
- Add emergency map integration
- Implement mobile responsiveness improvements
