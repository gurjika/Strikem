# Strikem

Strikem is a real-time platform for billiards enthusiasts, offering features like table reservations, player matchmaking, and game tracking with ratings. Built with a scalable backend and designed to provide a seamless user experience, this project was developed as part of a startup initiative.


## Tech Stack

- Backend Framework: Django Rest Framework (DRF)
- Real-Time Communication: Django Channels, Redis
- Task Management: Celery with Celery Beat for scheduled tasks
- Database: MySQL (hosted separately)
- Media Storage: AWS S3 Bucket
- Web Server: Nginx (reverse proxy and static file serving)
- Application Server: Gunicorn
- JWT: Used for authenticating WebSocket and WSGI traffic.

## Deployment and Hosting

- Gunicorn: Handles WSGI requests for HTTP traffic.
- Daphne: Handles ASGI requests for WebSocket traffic.
- Docker and Docker Compose: Orchestrates **separate containers for ASGI and WSGI apps**, databases, caching, and static file handling.
- DigitalOcean: Cloud platform for hosting PoolHub’s containers.

## Key Features

- **Real-time Messaging**: Utilizes Django Channels for WebSocket communication to enable real-time messaging between users.
- **Matchmaking System**: Implements a matchmaking feature where users can send and accept invitations to play, based on profiles  ratings and player current location, fostering community growth.
- **Reservation System**: Allows users to book reservations with notifications using Celery and Redis.
- **Game Tracking**: Track results, stats and ratings for games played.
- **Location Filtering**: Filters nearby pool halls and is used in matchmaking system to display active players nearby using Google Maps API.
- **Admin Panel**: Admin panel for pool hall staff to monitor reservations.

## MVP

Check out the **Frontend MVP** of the platform [here](https://strikem.vercel.app/home). 

## Built in Collaboration With

- This project was built in collaboration with [@4LL7N](https://github.com/4LL7N), who was responsible for developing the **React-based frontend**, designing and implementing the user interface and interactive components for the platform.


## Setup Instructions

To run this project locally:

1. Clone the repository (development branch):
    ```sh
    git clone -b dev https://github.com/gurjika/PoolHub.git
    ```

2. Change into the project directory:
    ```sh
    cd poolhub
    ```

3. Create a `.env` file and specify the required environment variables:
    ```env
    SECRET_KEY=your_django_secret_key
    DB_HOST=db
    DB_PASSWORD=your_db_password
    EMAIL_HOST_PASSWORD=your_email_password
    AWS_ACCESS_KEY_ID=your_aws_access_key
    AWS_SECRET_ACCESS_KEY=your_aws_secret_key
    AWS_STORAGE_BUCKET_NAME=bucket_name
    AWS_S3_REGION_NAME=region_name
    GOOGLE_MAPS_API_KEY=api_key_maps
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

