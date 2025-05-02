# DRF Media Library

A RESTful media management platform built with Django REST Framework that allows users to organize and rate movies, TV shows, and video games. Users can create personal collections and share ratings.

## Key Features

- Multi-type media support (Movies, TV Shows, Games)
- Rating system
- Personal collections management
- Custom User authentication

## Technology Stack

### Backend
- Python 3.13
- Django 5.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery

### Infrastructure
- Docker
- Docker Compose
- Nginx (production)
- Gunicorn (production)

## How to Run the Project Locally

### Setup Instructions

1. Clone this repository to any desirable place on your PC

2. Create a .env file based on .env.example and configure environment variables.

3. Start the project using Docker:
   docker-compose up -d --build

4. Once running, the project will be available at:
   - API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

## Access the Deployed Project

The project is deployed and accessible at: https://splashqq9.fvds.ru/docs/
