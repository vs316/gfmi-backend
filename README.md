# GFMI Insight Buddy - Backend API

## Overview

This is the FastAPI backend for the GFMI Insight Buddy application, providing full CRUD operations for survey data with comprehensive filtering capabilities.

## Features

- **Full CRUD Operations**: Create, Read, Update, Delete survey responses
- **Advanced Filtering**: Filter by teams, geography, medical data, HCPs, events, and surveys
- **Dremio Integration**: Direct SQL connection to Dremio data warehouse
- **Production-Ready**: Proper error handling, validation, and documentation
- **RESTful API**: Clean, intuitive API design
- **Auto-Generated Documentation**: Swagger/OpenAPI docs available at `/docs`

## Project Structure

```
gfmi-backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/                # Core configuration and database
│   ├── models/              # Pydantic models
│   ├── api/v1/endpoints/    # API endpoints
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── requirements.txt
└── .env                     # Environment variables
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your Dremio credentials:

```env
DREMIO_HOST=your-dremio-host
DREMIO_PORT=31010
DREMIO_USERNAME=your-username
DREMIO_PASSWORD=your-password
DREMIO_DATABASE=your-database
```

### 3. Run the Application

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Survey Operations

- `POST /api/v1/surveys/` - Create a new survey response
- `GET /api/v1/surveys/` - Get surveys with filtering
- `GET /api/v1/surveys/{id}` - Get specific survey
- `PUT /api/v1/surveys/{id}` - Update survey
- `DELETE /api/v1/surveys/{id}` - Delete survey

### Filter Operations

- `GET /api/v1/filters/options` - Get all filter options
- `GET /api/v1/filters/related` - Get related filter options

## Filter Categories

### Teams and Organizations
- MSL Names
- Titles (Director levels)
- Departments
- User Types

### Geographic
- Regions
- Countries/Geo IDs
- Territories

### Medical
- Tumor Types
- Products
- Product Expertise

### Healthcare Provider (HCP)
- Account Names
- Institutions
- Specialties
- Practice Settings

### Event & Engagement
- Channels
- Assignment Types

### Surveys
- Survey Names
- Questions

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Integration with Frontend

The backend is designed to work seamlessly with the React frontend. Key integration points:

1. **CORS Configuration**: Allows requests from frontend origins
2. **Filter API**: Provides dynamic filter options for sidebar
3. **Real-time Updates**: Supports real-time data updates
4. **Pagination**: Built-in pagination support

## Frontend Integration Example

```typescript
// Get filter options
const filterOptions = await fetch('/api/v1/filters/options');

// Get surveys with filters
const surveys = await fetch('/api/v1/surveys/?country_geo_id=GB-UK-Ireland&page=1&size=50');

// Create new survey
const newSurvey = await fetch('/api/v1/surveys/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(surveyData)
});
```

## Database Schema

The API expects a table with the following key columns:

- `survey_qstn_resp_id` (Primary Key)
- `survey_key`, `msl_key`, `account_key`
- Geographic: `country_geo_id`, `territory`, `region`
- Personnel: `msl_name`, `name`, `title`, `useremail`
- Survey Data: `survey_name`, `question`, `response`
- Medical: `product`, `product_expertise`
- Institution: `account_name`, `company`

## Development

### Adding New Filters

1. Add fields to `SurveyFilter` model in `app/models/filter.py`
2. Update `FilterOptions` model
3. Modify `FilterService` to include new filter logic
4. Update API endpoints to accept new parameters

### Adding New Endpoints

1. Create new endpoint in `app/api/v1/endpoints/`
2. Add to router in `app/api/v1/api.py`
3. Implement business logic in services

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

Set all required environment variables in your production environment.

### Health Checks

The API includes a health check endpoint at `/` that returns API status and version.
"""
}

# Write all files
for filepath, content in backend_files.items():
    # Create directory if it doesn't exist
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("✅ FastAPI Backend Structure Created Successfully!")
print("\nFiles created:")
for filepath in sorted(backend_files.keys()):
    print(f"  📄 {filepath}")

print(f"\n📊 Total files created: {len(backend_files)}")
print("\n🚀 Next steps:")
print("1. Navigate to the project directory")
print("2. Create a virtual environment: python -m venv venv")
print("3. Activate it: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
print("4. Install dependencies: pip install -r requirements.txt")
print("5. Configure your .env file with Dremio credentials")
print("6. Run the server: uvicorn app.main:app --reload")
print("7. Visit http://localhost:8080/docs for API documentation")