# LifeTrack – Health & Wellness Tracking System

## Project Description

LifeTrack is a health and wellness tracking web application that helps users keep track of their daily health habits and progress. Users can create an account, log in, and record their workouts, water intake, sleep, and nutrition.

The goal of this project is to create a simple and easy-to-use system where users can manage their health information and see their progress over time.

## Features

Current features include:

- Create a user account
- Log in and log out
- Login and password validation
- Forgot Password page and local password reset demonstration
- Track daily workouts and exercise duration
- Track water intake in milliliters (mL)
- Track sleep hours
- Track food intake and calories
- Save tracking information in SQLite
- View previous tracking records
- Delete saved tracking entries
- View daily totals and recent activities on the My Progress page

Planned features include:

- Create personal wellness goals
- View weekly progress charts
- View health and wellness trends

## Sprint 1 – User Accounts and Login

For Sprint 1, our main goal was to build the basic user account system and create the starting point for the application.

Completed features:

- Create Account page
- User registration
- Login page
- Login validation
- Password validation
- SQLite database for storing users
- Basic welcome/dashboard page

## Sprint 2 – Database and Daily Tracking

For Sprint 2, our main goal was to add daily health tracking features and connect them to our SQLite database.

Completed features:

- Created database tables for nutrition, workouts, water, and sleep
- Added a Nutrition page to record food names and calories
- Added a Workouts page to record workout types and duration
- Added a Water page to record daily water intake
- Added a Sleep page to record sleep hours
- Connected tracking entries to individual user accounts
- Saved tracking information in SQLite
- Displayed previously saved entries
- Added a three-dot menu to delete saved entries
- Created a My Progress page showing daily totals and recent activities
- Added a Forgot Password page and local password reset demonstration

Users can add tracking information, refresh the page, and still see their saved records because the information is stored in the database.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Git and GitHub

## How to Run the Project

1. Clone or download the project from GitHub.
2. Open the project folder in VS Code.
3. Make sure Python and Flask are installed.
4. Install any required Python packages.
5. Run the application:

   ```bash
   python app.py
   ```

6. Open the application in your browser.
7. Create an account or log in to start tracking your health activities.

## Current Status

Sprint 1 is complete, and the main features for Sprint 2 have been implemented.

Users can create accounts, log in, track their daily nutrition, workouts, water intake, and sleep, and view their saved information. They can also delete entries and view daily totals on the My Progress page.

The Forgot Password feature currently uses a local demonstration process rather than sending real password reset emails.

Future work will focus on improving the dashboard, adding personal wellness goals, and displaying weekly charts and trends.
