# Poolhub
A Poolhouse management system. 


## Technologies Used

- Django
- Django REST Framework
- Django Channels
- Celery
- Redis
- Bootstrap
- HTMX

## Features Implemented

- **Real-time Messaging**: Utilizes Django Channels for WebSocket communication to enable real-time messaging between users.
- **Matchmaking System**: Implements a matchmaking feature where users can send and accept invitations to play.
- **Reservation System**: Allows users to book reservations with notifications using Celery and Redis.
- **User Interfaces**: Designed with Bootstrap for responsive and user-friendly interfaces.
- **Database Integration**: Uses MySQL with Docker for database management.

## Work in Progress

This project is currently under development. Here are some features still in progress or planned:

- **Refined UI/UX**: Further refining user interfaces for better usability and responsiveness.
- **Performance Optimization**: Optimizing database queries and WebSocket handling for better performance.
- **Admin Panel**: Creating a tool that admins can use to manage poolhouses.
- **Game Session**: Allowing users to receive information about their game sessions.

## Setup Instructions

To run this project locally:

1. Clone the repository:
    ```sh
    git clone https://github.com/gurjika/PoolHub.git
    ```

2. Change into the project directory:
    ```sh
    cd poolhub
    ```

3. Create a `.env` file and specify the required environment variables:
    ```env
    PASSWORD=your_db_password
    HOST=mysql
    ```

4. Run the application using Docker Compose:
    ```sh
    docker-compose up -d
    ```

5. Run the database migrations:
    ```sh
    docker-compose run django python manage.py migrate
    ```

6. Create a superuser:
    ```sh
    docker-compose run django python manage.py createsuperuser
    ```

7. Access the development server at [http://localhost:8000](http://localhost:8000).development server.

