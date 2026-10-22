# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Display announcements that are currently within their active dates
- Let signed-in teachers create, edit, and delete announcements

## Getting Started

1. Start MongoDB at `mongodb://localhost:27017/` and install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/activities` | Get all activities and their details |
| POST | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity |
| GET | `/announcements` | List announcements currently active by date |
| GET | `/announcements/manage` | List all announcements; requires a bearer session token |
| POST | `/announcements` | Create an announcement; requires a bearer session token |
| PUT | `/announcements/{announcement_id}` | Update an announcement; requires a bearer session token |
| DELETE | `/announcements/{announcement_id}` | Delete an announcement; requires a bearer session token |
| POST | `/auth/login?username=...&password=...` | Sign in and receive a session token |
| GET | `/auth/check-session` | Validate a session token sent as `Authorization: Bearer <token>` |
| POST | `/auth/logout` | Revoke the current bearer session token |

Announcement requests use a JSON body with a required `message` and `expiration_date` (`YYYY-MM-DD`), and an optional `start_date` (`YYYY-MM-DD`). Expiration cannot be before the start date.

## Data Model

The application stores its data in MongoDB:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Announcements** - Uses a generated identifier and stores the message, optional start date, required expiration date, and creator.

3. **Teachers and sessions** - Teacher credentials are stored as password hashes. Session bearer tokens are stored as hashes and expire after 12 hours.
