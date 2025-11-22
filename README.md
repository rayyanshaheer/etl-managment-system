# ETL Management System

A complete, fully functional ETL (Extract, Transform, Load) Pipeline Management System built with Flask, SQLAlchemy, Pandas, and SQLite.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

- ✅ **User Authentication** - Secure login/logout with password hashing
- ✅ **Multiple Data Sources** - CSV file uploads and API endpoints
- ✅ **Complete ETL Pipeline** - Extract, Transform, Load in one click
- ✅ **Data Visualization** - View transformed data in responsive tables
- ✅ **Detailed Logging** - Track every ETL step with timestamps
- ✅ **Job Management** - Create, view, and delete ETL jobs
- ✅ **Modern UI** - Bootstrap 5 responsive design
- ✅ **Database Integration** - SQLite with SQLAlchemy ORM

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [ETL Pipeline](#etl-pipeline)
- [API Testing](#api-testing)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)

## 🏃 Quick Start

```bash
# Navigate to project directory
cd your-etl-project

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 run.py

# Open browser and visit
http://localhost:5000
```

That's it! The database and upload folders are created automatically on first run.

## 💡 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Step-by-Step Installation

1. **Clone or download the project**
   ```bash
   cd your-etl-project
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python3 run.py
   ```

4. **Access the application**
   - Open your browser
   - Navigate to `http://localhost:5000`
   - Register a new account
   - Start creating ETL jobs!

## 📖 Usage

### 1. Register/Login

- Navigate to `http://localhost:5000`
- Click **"Register here"** to create a new account
- Fill in username, email, and password
- Login with your credentials

### 2. Create ETL Job

#### Option A: CSV File Upload

1. Click **"Create New Job"** or **"New Job"** button
2. Enter **Job Name** (e.g., "Employee Data")
3. Add **Description** (optional)
4. Select **"CSV File Upload"**
5. Click **"Choose File"** and upload your CSV file
6. Click **"Create Job"**

#### Option B: API Endpoint

1. Click **"Create New Job"**
2. Enter **Job Name** (e.g., "GitHub Users")
3. Add **Description** (optional)
4. Select **"API Endpoint"**
5. Enter **API URL** (e.g., `https://jsonplaceholder.typicode.com/users`)
6. Select **Response Format** (JSON or CSV)
7. Click **"Create Job"**

### 3. Run ETL Pipeline

1. Go to your job's detail page
2. Click the **"Run ETL"** button
3. Watch the pipeline execute:
   - ⚡ **Extract** - Data is pulled from source
   - 🔧 **Transform** - Data is cleaned and standardized
   - 💾 **Load** - Data is saved to SQLite database
4. View success message with row counts

### 4. View Results

- **View Data** - Click to see transformed data in a table
- **View Logs** - Click to see detailed execution logs with timestamps

### 5. Monitor ETL Runs

- Each job shows run history
- Track status: Success, Failed, or Running
- View rows extracted, transformed, and loaded
- Check error messages if pipeline fails

## 🔄 ETL Pipeline

The ETL pipeline consists of three stages that run automatically when you click "Run ETL":

### 📥 Extract Stage

**Purpose**: Pull data from the source

**CSV Source**:
- Reads CSV file using pandas
- Validates file format
- Counts rows extracted
- Logs file path and status

**API Source**:
- Sends HTTP GET request to API URL
- Handles JSON and CSV responses
- Parses nested JSON structures
- Handles arrays and objects
- Logs API response status

**Output**: Pandas DataFrame with raw data

### 🔧 Transform Stage

**Purpose**: Clean and standardize the data

**Operations**:
1. **Clean Column Names**
   - Convert to lowercase
   - Replace spaces with underscores
   - Remove special characters
   - Example: `"First Name"` → `"first_name"`

2. **Remove Empty Rows**
   - Drop rows that are completely empty
   - Reset DataFrame index
   - Log rows removed

3. **Data Validation**
   - Check for valid column names
   - Ensure data integrity
   - Log transformation statistics

**Output**: Cleaned Pandas DataFrame

### 💾 Load Stage

**Purpose**: Save transformed data to database

**Operations**:
1. Create unique table name for the job
2. Drop existing table if present (replace mode)
3. Write DataFrame to SQLite using pandas `to_sql()`
4. Verify rows loaded
5. Log table name and row count

**Output**: Data stored in SQLite database

### 📊 Logging System

Every stage logs:
- ✓ Start/completion messages
- ✓ Row counts at each stage
- ✓ Success confirmations
- ✓ Error messages with details
- ✓ Timestamps for all events

## 🧪 API Testing

Here are public APIs you can use to test the system:

### JSON APIs

```
https://jsonplaceholder.typicode.com/users
https://jsonplaceholder.typicode.com/posts
https://jsonplaceholder.typicode.com/todos
https://jsonplaceholder.typicode.com/comments
https://api.github.com/users
```

### CSV APIs

```
https://people.sc.fsu.edu/~jburkardt/data/csv/addresses.csv
https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv
https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv
```

### Example: Test with JSONPlaceholder

1. Create new job
2. Name: "User Data from API"
3. Select "API Endpoint"
4. URL: `https://jsonplaceholder.typicode.com/users`
5. Format: JSON
6. Click "Create Job"
7. Click "Run ETL"
8. View the 10 users loaded into your database!

## 📁 Project Structure

```
etl-managment-system/
├── app/
│   ├── __init__.py              # Flask app factory with blueprints
│   ├── models.py                # SQLAlchemy database models
│   ├── utils.py                 # Utility functions (file upload, URL validation)
│   │
│   ├── etl/                     # ETL Pipeline Modules
│   │   ├── __init__.py
│   │   ├── extract.py           # Data extraction (CSV & API)
│   │   ├── transform.py         # Data transformation & cleaning
│   │   └── load.py              # Data loading to SQLite
│   │
│   ├── routes/                  # Flask Blueprints
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── main.py              # Dashboard routes
│   │   ├── jobs.py              # Job management routes
│   │   └── etl.py               # ETL execution routes
│   │
│   └── templates/               # Jinja2 HTML Templates
│       ├── base.html            # Base template with navigation
│       ├── index.html           # Homepage/dashboard
│       ├── dashboard.html       # Statistics dashboard
│       │
│       ├── auth/
│       │   ├── login.html       # Login page
│       │   └── register.html    # Registration page
│       │
│       ├── jobs/
│       │   ├── create.html      # Job creation form
│       │   ├── list.html        # Jobs list table
│       │   └── view.html        # Job details & run history
│       │
│       └── etl/
│           ├── view_data.html   # Transformed data viewer
│           ├── view_logs.html   # ETL execution logs
│           └── logs_overview.html # All logs overview
│
├── uploads/                     # CSV file uploads (auto-created)
├── config.py                    # Flask configuration
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── sample_data.csv              # Sample test data
├── test_system.py               # System verification script
├── README.md                    # This file
├── QUICKSTART.md                # Quick start guide
└── PROJECT_STATUS.md            # Project verification report
```

## 🗄️ Database Schema

The system uses SQLite with SQLAlchemy ORM. Five main tables:

### Users Table
```sql
id              INTEGER PRIMARY KEY
username        VARCHAR(80) UNIQUE NOT NULL
email           VARCHAR(120) UNIQUE NOT NULL
password_hash   VARCHAR(200) NOT NULL
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

### Jobs Table
```sql
id              INTEGER PRIMARY KEY
name            VARCHAR(100) NOT NULL
description     TEXT
user_id         INTEGER FOREIGN KEY → users.id
table_name      VARCHAR(100) UNIQUE
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

### DataSources Table
```sql
id              INTEGER PRIMARY KEY
job_id          INTEGER FOREIGN KEY → jobs.id
source_type     VARCHAR(20) NOT NULL  -- 'csv' or 'api'
file_path       VARCHAR(500)          -- For CSV uploads
api_url         VARCHAR(500)          -- For API sources
api_format      VARCHAR(20)           -- 'json' or 'csv'
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

### ETLRuns Table
```sql
id                INTEGER PRIMARY KEY
job_id            INTEGER FOREIGN KEY → jobs.id
status            VARCHAR(20) NOT NULL  -- 'running', 'success', 'failed'
started_at        DATETIME DEFAULT CURRENT_TIMESTAMP
completed_at      DATETIME
rows_extracted    INTEGER DEFAULT 0
rows_transformed  INTEGER DEFAULT 0
rows_loaded       INTEGER DEFAULT 0
error_message     TEXT
```

### ETLLogs Table
```sql
id              INTEGER PRIMARY KEY
etl_run_id      INTEGER FOREIGN KEY → etl_runs.id
stage           VARCHAR(20) NOT NULL  -- 'extract', 'transform', 'load'
message         TEXT NOT NULL
log_level       VARCHAR(20) DEFAULT 'info'  -- 'info', 'warning', 'error'
timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///etl_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
```

### Environment Variables

You can override settings using environment variables:

```bash
export SECRET_KEY='production-secret-key'
export DATABASE_URL='postgresql://user:pass@localhost/etldb'
```

## 📸 Screenshots

### Dashboard
- View all your ETL jobs at a glance
- See statistics: total jobs, successful runs
- Quick access to create new jobs

### Job Creation
- Simple form for CSV or API sources
- File upload with drag-and-drop support
- URL validation for API endpoints

### ETL Execution
- Real-time status updates
- Progress tracking through stages
- Detailed row counts

### Data Viewer
- Responsive table display
- First 100 rows preview
- Column names and statistics

### Logs Viewer
- Color-coded by severity (info, warning, error)
- Timestamps for each event
- Stage-by-stage breakdown

## 🛠️ Tech Stack

### Backend
- **Flask 3.0.0** - Web framework
- **SQLAlchemy 3.1.1** - ORM and database toolkit
- **Flask-Login 0.6.3** - User session management
- **Pandas 2.1.3** - Data processing and ETL operations
- **Requests 2.31.0** - HTTP client for API calls
- **Werkzeug 3.0.1** - WSGI utilities and password hashing

### Frontend
- **Bootstrap 5.3** - CSS framework
- **Bootstrap Icons** - Icon library
- **Jinja2** - Template engine

### Database
- **SQLite** - Embedded database (development)
- Can be switched to PostgreSQL/MySQL for production

## 🔒 Security Features

1. **Password Security**
   - Werkzeug password hashing (scrypt algorithm)
   - No plain text password storage
   - Salted hashes

2. **File Upload Security**
   - File type validation (only .csv and .txt)
   - Secure filename generation
   - File size limits (16MB)

3. **API Security**
   - URL validation
   - Request timeout (30 seconds)
   - Error handling for failed requests

4. **Session Management**
   - Flask-Login integration
   - Secure session cookies
   - User isolation (users only see their own jobs)

5. **Input Validation**
   - Form validation on client and server side
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection (Jinja2 auto-escaping)

## 🧪 Testing

Run the verification script to test all components:

```bash
python3 test_system.py
```

This tests:
- ✓ Module imports
- ✓ Flask app creation
- ✓ Database models
- ✓ Utility functions
- ✓ ETL modules
- ✓ Route registration
- ✓ Template files

## 🚀 Deployment

### Development Mode (Current)
```bash
python3 run.py
```

### Production Deployment

1. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
   ```

2. **Set environment variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY='your-production-secret-key'
   ```

3. **Use PostgreSQL instead of SQLite**
   ```bash
   export DATABASE_URL='postgresql://user:pass@localhost/etldb'
   ```

4. **Add Nginx reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 📝 Sample Data

A sample CSV file (`sample_data.csv`) is included:

```csv
name,age,city,email,salary
John Doe,30,New York,john@example.com,75000
Jane Smith,25,Los Angeles,jane@example.com,65000
Bob Johnson,35,Chicago,bob@example.com,80000
Alice Williams,28,Houston,alice@example.com,70000
Charlie Brown,32,Phoenix,charlie@example.com,72000
```

Use this to test CSV upload functionality.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill existing Flask process
pkill -f "python3 run.py"
# Or use a different port
export FLASK_RUN_PORT=5001
python3 run.py
```

### Database Locked
```bash
# Remove database and restart
rm etl_system.db
python3 run.py
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Request Fails
- Check internet connection
- Verify API URL is accessible
- Check API response format matches selection (JSON/CSV)

## 📚 Learning Resources

This project demonstrates:
- Flask application factory pattern
- SQLAlchemy ORM relationships
- Flask-Login authentication
- Blueprint-based routing architecture
- Jinja2 templating
- Pandas data manipulation
- RESTful API design
- File upload handling
- Error handling strategies

## 🤝 Contributing

This is an educational project. Feel free to:
- Fork the repository
- Add new features
- Improve documentation
- Report bugs
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the QUICKSTART.md guide
3. Check PROJECT_STATUS.md for verification details

## 🎉 Acknowledgments

- Built with Flask, SQLAlchemy, Pandas, and Bootstrap
- Sample APIs from JSONPlaceholder and other public sources
- Icons from Bootstrap Icons

## 📊 Project Statistics

- **Total Files**: 30+
- **Lines of Code**: 2,500+
- **Python Modules**: 10
- **HTML Templates**: 10
- **Database Models**: 5
- **Routes**: 15+
- **Dependencies**: 6

---

**Version**: 1.0.0  
**Last Updated**: November 23, 2025  
**Status**: Production Ready ✅

Made with ❤️ using Flask, SQLAlchemy, Pandas, and Bootstrap
