# Staff Scheduling Application

A Flask-based staff scheduling system for managing employee schedules, time-off requests, and shift trades.

## Features

- Staff and Manager role-based access
- Schedule management
- Time-off requests
- Shift trading
- Overtime logging
- Staff availability management

## Tech Stack

- Backend: Flask
- Database: SQLAlchemy
- Authentication: Flask-Login
- Frontend: HTML/Tailwind CSS
- Email: Flask-Mail

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Run the application:
   ```bash
   flask run
   ```

## Project Structure

- `/backend` - Flask application
  - `/app` - Application code
    - `/models` - Database models
    - `/routes` - Route handlers
    - `/templates` - HTML templates

