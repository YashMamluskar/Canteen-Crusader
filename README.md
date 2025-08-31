# 🍔 Canteen Crusader

Canteen Crusader is a full-stack web application designed as a food review platform for a campus canteen. It's built with a scalable Python Flask backend and a responsive Bootstrap 5 frontend.

## Key Features

-   **User Roles**: Full authentication system with distinct **Admin** and **User** roles.
-   **Review System**: Users can submit reviews with a 1-5 star rating, text, and optional image uploads.
-   **Sentiment Analysis**: Automatically analyzes review text using **TextBlob** to provide deeper insights beyond star ratings.
-   **Personalization**: Users can **favorite** items and receive **personalized recommendations** based on their rating history.
-   **Dynamic Homepage**: Features top-rated items, trending items, and top reviewers.
-   **Admin Dashboard**: Admins can add new menu items and moderate reviews.
-   **Database Seeding**: Includes a `seed.py` script to quickly populate the database with sample data for development and testing.

## Tech Stack

-   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
-   **Database**: SQLite (with Flask-Migrate)
-   **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
-   **Libraries**: TextBlob for sentiment analysis

## How to Run This Project

1.  Clone the repository and navigate into the project directory.
2.  Create and activate a virtual environment.
3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  (Optional but Recommended) Populate the database with sample data:
    ```bash
    python seed.py
    ```
5.  Run the application:
    ```bash
    flask run
    ```
6.  Open your browser and go to `http://127.0.0.1:5000`.
