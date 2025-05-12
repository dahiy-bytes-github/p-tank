# P-Tank: Predictive Septic Tank Monitoring System

P-Tank is a full-stack web application for real-time septic tank monitoring.  
It features a **React** frontend and a **Flask** REST API backend with **JWT authentication**, **user management**, **sensor data analytics**, and **notifications**.

---

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [API Overview](#api-overview)
- [How to Use the Live Website](#how-to-use-the-live-website)
- [Security Notes](#security-notes)
- [License](#license)

---

## Features
- Secure **JWT-based** user authentication
- Admin and normal user roles
- Sensor data creation and viewing
- Notifications for critical tank conditions
- Admin user management
- Predictive analytics with machine learning
- Responsive **React** frontend

---

## Architecture
- **Frontend:** React (`client/`)
- **Backend:** Flask, Flask-RESTful, Flask-JWT-Extended (`server/`)
- **Database:** PostgreSQL
- **Deployment:** Render.com

---

## Project Structure
p-tank/
├── client/ # React frontend
├── server/ # Flask backend
├── .gitignore
└── README.md

---

## Getting Started

### Backend Setup (Flask)

1. Clone the repository:
    ```
    git clone https://github.com/dahiy-bytes-github/p-tank
    cd p-tank/server
    ```

2. Install dependencies:
    ```
    pipenv install --dev
    pipenv shell
    ```

3. Configure environment variables:  
   Create a `.env` file (see [Environment Variables](#environment-variables)).

4. Initialize the database:
    ```
    flask db upgrade
    ```

5. Run the backend:
    ```
    flask run
    ```

---

### Frontend Setup (React)

1. Install dependencies:
    ```
    cd ../client
    npm install
    ```

2. Configure environment variables:  
   Create a `.env` file (see [Environment Variables](#environment-variables)).

3. Run the frontend:
    ```
    npm start
    ```

---

## Environment Variables

### Backend (`server/.env`)
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465


### Frontend (`client/.env`)
REACT_APP_API_BASE_URL=http://localhost:5000

> **Note:** For production, set `REACT_APP_API_BASE_URL` to your backend’s deployed URL.

---

## Deployment (Render.com)

### Backend (Flask)
- **Root Directory:** `server`
- **Build Command:**

pip install -r requirements.txt
- **Start Command:**
gunicorn app:app
- **Environment Variables:** Copy from your `.env` file.
- **Procfile:** Inside `server/` with content:
web: gunicorn app:app


### Frontend (React)
- **Root Directory:** `client`
- **Build Command:**

npm install && npm run build
- **Publish Directory:** `build`
- **Environment Variables:** Set `REACT_APP_API_BASE_URL` to your deployed backend URL.

---

## API Overview

### Authentication
- `POST /auth/register` — Register a new user
- `POST /auth/login` — Login and receive JWT tokens
- `POST /auth/logout` — Logout (JWT blacklist)
- `POST /refresh` — Refresh access token

### Users (Admin Only)
- `GET /users` — List all users
- `PUT /users/<user_id>` — Update a user
- `DELETE /users/<user_id>` — Delete a user

### Sensor Readings
- `GET /sensorreadings` — List or filter readings
- `POST /sensor-readings/create` — Create a new reading

### Notifications
- `GET /notifications` — Get user notifications
- `PATCH /notifications/<user_notification_id>` — Mark notification as read

---

## How to Use the Live Website

Visit the live app here:  
👉 [**P-Tank Live Website**](https://p-tank-fren.onrender.com)

Steps:
1. **Register** a new user account.
2. **Login** using your new credentials.
3. To test **admin privileges**, login with:
 - **Email:** `alice@example.com`
 - **Password:** `test123`
4. Explore:
 - View sensor readings
 - View notifications
 - Manage users (only if logged in as admin)

---

## Security Notes
- Never commit `.env` files or secrets to version control.
- Use strong and unique `SECRET_KEY` and `JWT_SECRET_KEY` values.
- Restrict CORS origins to your frontend URL in production.
- Immediately rotate credentials if exposed.

---

## License
This project is licensed under the **MIT License**.


