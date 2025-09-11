# Videoflix Backend

[![Python](https://img.shields.io/badge/Python-3.13.1-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.4-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://www.docker.com/)

## 📌 Project Description

The **Videoflix Backend** powers the **Videoflix** video streaming platform, inspired by Netflix.  
Registered users can stream videos across multiple categories using **HLS**, with videos available in multiple resolutions. Admin users can manage the video library and platform content through a dedicated admin panel.  

The backend is fully containerized with **Docker Compose** for seamless deployment and development.

> 🔗 **[Frontend Repository (V1.0.0)](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)**  
> 🔗 **[Live Version](https://annafritz.de/videoflix)** <br>
> 📖 **[API-Dokumentation (Swagger)](https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=videoflix)**

---

## 🛠 Installation & Setup

### System Requirements

- **Python:** 3.13.1
- **Database:** PostgreSQL
- **Redis** (runs via Docker in this setup)
- **Docker & Docker Compose** (Docker Desktop required on Windows/Mac, Docker Engine on Linux)

### Dependencies (from `requirements.txt`)
```sh
# Core Frameworks
Django==5.2.4
djangorestframework==3.16.0
djangorestframework-simplejwt==5.5.0

# Database & Caching
psycopg2-binary==2.9.10
django-redis==6.0.0
redis==6.2.0
django-rq==3.0.1
rq==2.4.0 

# Server & Static Files
gunicorn==23.0.0
whitenoise==6.9.0
django-cors-headers==4.7.0

# Media Handling
pillow==11.3.0

# Testing & Coverage
pytest==8.4.1
pytest-django==4.11.1
pytest-cov==6.2.1
coverage==7.10.3

# Environment & Utilities
python-dotenv==1.1.1
````

---

## 📦 Docker Compose Setup

This project uses **Docker Compose** for easy deployment. Containers include:

- `db` → PostgreSQL
- `redis` → Redis server
- `web` → Django backend running with Gunicorn
- `worker` → Django-RQ worker for processing background jobs
- `test` → Container for running tests with pytest and coverage

---

### Installation Steps

1. Clone the repository:
   ```sh
   git clone https://github.com/Anna-Fritz/videoflix_backend.git
   cd videoflix_backend

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
   ```sh
   pip install -r requirements.txt

4. Copy `.env.template` to `.env` and update with your environment variables:
   ```sh
   cp .env.template .env

5. Build web container first, then start all containers (including DB, Redis, Django backend, and Django-RQ worker):
   ```sh
   docker compose build web
   docker compose up
   ```

   This will also run migrations automatically for the backend.

6. Stop container
   ```sh
   docker compose down

---


## 🧪 Running Tests

Tests are executed with **pytest** and coverage reporting inside the `test` container:
```sh
docker compose -f docker-compose.test.yml up
````

This will:

- Run the test suite with pytest
- Generate a coverage report in the terminal
- Create a coverage.xml file in the project root (used for CI/CD and coverage badges)


---


## 📝 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

- **Share:** You may copy and redistribute the material in any format or medium.
- **Adapt:** You may remix, transform, and build upon the material.
- **Non-Commercial:** You may not use the material for commercial purposes.

For full details, see the [official license documentation](https://creativecommons.org/licenses/by-nc/4.0/).

---

## 👩‍💻 Author

Developed and maintained by [Anna](https://github.com/Anna-Fritz).
