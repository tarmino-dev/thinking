# Image Upload API

A cloud-based backend service for uploading, processing, and storing images using FastAPI and AWS.

## Overview

This project is a backend service that allows users to upload images, process them, and store them in a cloud environment.

The application is built with `FastAPI` and follows a modular architecture, separating API logic, business logic, and infrastructure components. Image processing (resizing and thumbnail generation) runs **asynchronously** in a `Celery` worker with `Redis` as the message broker and result backend: `POST /upload` enqueues a background task and returns immediately with a `task_id`, and the client polls `GET /tasks/{task_id}` for the result. Processed images are stored in `AWS S3`, while metadata is persisted in a `PostgreSQL` database hosted on `AWS RDS`.

The service includes user authentication using `JWT` and demonstrates a complete cloud-based workflow, including containerization with `Docker` and automated deployment using `GitHub Actions`.

This project is designed to showcase practical experience with backend development, cloud services, and deployment pipelines in a production-like environment.

## Features

* User registration and authentication using `JWT`
* Secure password storage with hashing (`bcrypt`)
* Image upload via REST API endpoint (`/upload`)
* Asynchronous image processing with `Celery` and `Redis`:

  * Upload enqueues a background task and returns a `task_id`
  * Task status/result retrieved via `GET /tasks/{task_id}`
* Image processing (in the worker):

  * Automatic resizing (max dimensions limit)
  * Thumbnail generation
* Cloud storage integration:

  * Images stored in `AWS S3`
  * Unique file naming using `UUID`
* Database integration:

  * Metadata stored in `PostgreSQL` (`AWS RDS`)
* Protected endpoints:

  * Upload requires a valid authentication token
  * Image listing/retrieval is scoped to the authenticated user (users see only their own images)
* Containerized application using `Docker` and `docker-compose`
* Environment-based configuration using `.env`
* Automated deployment with `GitHub Actions` (CI/CD pipeline)
* Modular project structure (`api`, `services`, `db`, `core`)

## Tech Stack

### Backend

* `Python`
* `FastAPI`
* `SQLAlchemy`

### Database

* `PostgreSQL`
* `AWS RDS`

### Cloud

* `AWS EC2` (application hosting)
* `AWS S3` (file storage)

### DevOps

* `Docker`
* `docker-compose`
* `GitHub Actions` (CI/CD)

### Security

* `JWT` (authentication)
* `passlib` (`bcrypt` password hashing)

### Image Processing

* `Pillow`

### Asynchronous Processing

* `Celery` (task queue)
* `Redis` (message broker and result backend)

## Architecture

The application follows a modular and layered architecture, separating concerns between API, business logic, data access, and infrastructure configuration.

### Structure

* `app/api` — API layer (routes, request handling, dependencies)
* `app/services` — business logic (file storage, image processing)
* `app/db` — database layer (models, session, CRUD operations)
* `app/core` — configuration and security (settings, JWT, hashing)
* `app/schemas` — data validation and serialization (Pydantic models)
* `app/celery_app.py` — Celery application (broker and result backend configuration)
* `app/tasks.py` — background tasks (asynchronous image processing)

### Data Flow

1. A client sends `POST /upload` with an image (and a valid `JWT`)
2. Authentication is verified via `JWT`
3. The API reads the file bytes and enqueues a `process_image` task on `Redis`, then returns a `task_id`
4. The `Celery` worker picks up the task and:

   * processes the image (`resize`, `thumbnail`)
   * uploads it to `AWS S3`
   * stores metadata (file URL, filename, user reference) in `PostgreSQL` (`AWS RDS`)
   * the task result is saved to the `Redis` result backend
5. The client polls `GET /tasks/{task_id}` until the task reports `SUCCESS` with the created image record
6. Read endpoints (`GET /images`, `GET /images/{id}`) return metadata directly from `PostgreSQL`

## Architecture Diagram

```
                ┌───────────────┐
                │     Client    │
                │ (Browser/API) │
                └───────┬───────┘
                        │ HTTP Requests
                        ▼
              ┌───────────────────┐   enqueue task   ┌───────────────┐
              │    FastAPI App    │ ───────────────► │     Redis     │
              │(Docker on AWS EC2)│ ◄─────────────── │ (broker +     │
              └─────────┬─────────┘   task status    │  result store)│
                        │                            └───────┬───────┘
                        │                                    │ consume task
                        │                                    ▼
                        │                          ┌───────────────────┐
                        │                          │   Celery Worker   │
                        │                          │(Docker on AWS EC2)│
                        │                          └─────────┬─────────┘
                        │                                    │
                        │  read metadata      write image + metadata
                        ▼                                    ▼
        ┌───────────────┴───────────────────────────────────┴───────┐
        │                                                            │
        ▼                                                            ▼
┌───────────────┐                                          ┌───────────────┐
│   AWS S3      │                                          │   AWS RDS     │
│ (File Storage)│                                          │ (PostgreSQL)  │
└───────────────┘                                          └───────────────┘

```

### Deployment Context

* The application is deployed on `AWS EC2`
* Containers are managed via `docker-compose`
* CI/CD pipeline (`GitHub Actions`) automates deployment on each push

## API Endpoints

### Authentication

#### `POST /register`

Register a new user.

Request body:

```json id="q9p3zb"
{
  "username": "string",
  "password": "string"
}
```

Response:

```json id="5m2h6n"
{
  "msg": "user created"
}
```

---

#### `POST /login`

Authenticate user and receive a JWT token.

Request body:

```json id="2z9k1x"
{
  "username": "string",
  "password": "string"
}
```

Response:

```json id="7x8c4a"
{
  "access_token": "jwt_token"
}
```

---

### Images

#### `POST /upload`

Upload an image (requires authentication).

Headers:

```id="r2k8pz"
Authorization: Bearer <JWT_TOKEN>
```

Request:

```id="v8n3lw"
multipart/form-data
file: <image_file>
```

The image is processed asynchronously. The endpoint enqueues a background task and returns a `task_id` immediately (HTTP `200`); the image record is created by the worker once processing completes.

Response:

```json id="m4c1qx"
{
  "task_id": "8d5c1f2a-3b47-4e9a-9c1d-2f6b7a0e1234"
}
```

---

#### `GET /tasks/{task_id}`

Retrieve the status and result of a background processing task (requires authentication).

While the task is running, `status` is `PENDING`/`STARTED` and `result` is `null`. Once finished, `status` is `SUCCESS` and `result` contains the created image record.

Response:

```json id="t1a2s3"
{
  "task_id": "8d5c1f2a-3b47-4e9a-9c1d-2f6b7a0e1234",
  "status": "SUCCESS",
  "result": {
    "id": 1,
    "filename": "example.jpg",
    "path": "https://s3.amazonaws.com/..."
  }
}
```

---

#### `GET /images`

Retrieve the list of images owned by the authenticated user (requires authentication).

Response:

```json id="k7t9fj"
[
  {
    "id": 1,
    "filename": "example.jpg",
    "path": "https://s3.amazonaws.com/...",
    "user_id": 1
  }
]
```

---

#### `GET /images/{image_id}`

Retrieve a single image owned by the authenticated user (requires authentication). Returns `404 Not Found` if the image does not exist or belongs to another user.

Response:

```json id="p3h6zn"
{
  "id": 1,
  "filename": "example.jpg",
  "path": "https://s3.amazonaws.com/...",
  "user_id": 1
}
```

## Authentication

* The application uses `JWT` (JSON Web Tokens) for stateless authentication.
* Authentication is implemented using dependency injection (`Depends`)
* Invalid or expired tokens result in `403 Forbidden` responses
* The system is designed to be stateless (no server-side session storage)

### How it works

1. A user registers via `POST /register`
2. The user logs in via `POST /login`
3. If credentials are valid, the server returns a `JWT` access token
4. The client includes this token in subsequent requests to protected endpoints

---

### Using the Token

To access protected endpoints (e.g., `/upload`), include the token in the request header:

```id="a1b2c3"
Authorization: Bearer <JWT_TOKEN>
```

---

### Token Generation

* Tokens are generated using `python-jose`
* Signed with a secret key (`SECRET_KEY`)
* Use the `HS256` algorithm
* Include expiration time (`exp` claim)

---

### Password Security

* Passwords are hashed using `bcrypt` via `passlib`
* Plain-text passwords are never stored
* Password verification is handled securely during login

## Environment Variables

The application uses environment variables for configuration. All variables are defined in a `.env` file and loaded into the application at runtime.

### Required Variables

| Variable       | Description                              | Default                                       |
| -------------- | ---------------------------------------- | --------------------------------------------- |
| `DATABASE_URL` | PostgreSQL connection string (`AWS RDS`) |                                               |
| `SECRET_KEY`   | Secret key used for `JWT` signing        | `supersecret`                                 |

---

### AWS Configuration

| Variable                | Description    | Default                |
| ----------------------- | -------------- | ---------------------- |
| `AWS_ACCESS_KEY_ID`     | AWS access key |                        |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |                        |
| `AWS_S3_BUCKET`         | S3 bucket name |                        |
| `AWS_REGION`            | AWS region     | `eu-central-1`         |

---

### Storage Configuration

| Variable       | Description                       | Default   |
| -------------- | --------------------------------- | --------- |
| `STORAGE_TYPE` | Storage backend (`local` or `s3`) | `local`   |
| `UPLOAD_DIR`   | Local upload directory            | `uploads` |

---

### Task Queue Configuration (Celery / Redis)

| Variable                | Description                          | Default                    |
| ----------------------- | ------------------------------------ | -------------------------- |
| `CELERY_BROKER_URL`     | Redis URL used as the message broker | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis URL used as the result backend | `redis://localhost:6379/0` |

In production (where `backend` and `worker` run as Docker Compose services), set the host to
the Redis service name: `redis://redis:6379/0`. Locally, the default `localhost` value works
when Redis is exposed on port `6379` (see **Local Development**).

---

### Example `.env`

```env
DATABASE_URL=postgresql://user:password@your_database_host:5432/postgres
SECRET_KEY=my-secure-app-secret-key

AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket_name
AWS_REGION=your_region

STORAGE_TYPE=s3
UPLOAD_DIR=uploads

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Local Development

Ensure `Docker` and `docker-compose` are installed.

Follow the steps below to run the project locally using `Docker`.

### 1. Clone only the image_upload_api branch

```bash
git clone -b image_upload_api https://github.com/tarmino-dev/thinking.git
cd thinking/fun_projects/image_upload_api
```

---

### 2. Create `.env` File

Create a `.env` file in the project root and configure the required environment variables.

Refer to the example configuration in the **Environment Variables** section.

---

### 3. Start local infrastructure (Redis + PostgreSQL)

Local-only services live in `docker-compose.dev.yml` (kept separate from the production
`docker-compose.yml`). Start them with:

```bash
docker compose -f docker-compose.dev.yml up -d
```

This runs Redis (broker/result backend) and a local PostgreSQL matching the default
`DATABASE_URL` (`postgresql://user:password@localhost:5432/app_db`).

---

### 4. Install dependencies and run the app + worker

The project uses a virtual environment. Install dependencies, then run the API and the
Celery worker in two separate terminals:

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt

# Terminal A — Celery worker
./venv/bin/celery -A app.celery_app.celery_app worker --loglevel=info

# Terminal B — FastAPI app
./venv/bin/python -m uvicorn app.main:app --reload
```

---

### 5. Access the API

Open your browser and navigate to:

```text
http://localhost:8000/docs
```

This will open the interactive Swagger UI where you can test all endpoints.

---

### Notes

* For local development, set `STORAGE_TYPE=local` to store files on disk (no AWS needed);
  `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` default to `localhost` and work with the Redis
  from `docker-compose.dev.yml`.
* Both the API and the worker must be running for uploads to complete: the API enqueues the
  task, and the worker processes it.
* If using `STORAGE_TYPE=s3`, make sure your AWS credentials are correctly configured.

## Deployment

The application is deployed on `AWS EC2` using `Docker` and `docker-compose`, with automated deployment via `GitHub Actions`.

### Deployment Flow

1. Code is pushed to the repository (branch: `image_upload_api`)
2. `GitHub Actions` workflow is triggered
3. The workflow:

   * copies project files to the EC2 instance via `SSH`
   * connects to the server
   * runs deployment commands:

     ```bash
     docker-compose pull || true
     docker-compose down
     docker-compose up --build -d
     ```
4. The application is rebuilt and restarted on the server

---

### Server Setup

* The application runs on an `AWS EC2` instance
* `Docker` and `docker-compose` are installed on the server
* The production `docker-compose.yml` runs three services: `backend` (FastAPI), `redis`
  (broker/result backend), and `worker` (Celery). All use `restart: unless-stopped` so they
  come back automatically after an instance reboot (ensure the Docker daemon is enabled on boot:
  `systemctl is-enabled docker`)
* Environment variables are managed via a `.env` file on the server
* The API is exposed on port `8000`

---

### CI/CD Configuration

* Secrets are stored securely in the repository settings:

  * `EC2_HOST`
  * `EC2_USER`
  * `EC2_SSH_KEY`
* The workflow uses:

  * `scp` to transfer files
  * `ssh` to execute remote commands

## AWS Integration

The application leverages several `AWS` services to provide scalable storage, reliable database management, and cloud-based deployment.

### Services Used

* `AWS S3` — object storage for uploaded images
* `AWS RDS` — managed PostgreSQL database
* `AWS EC2` — hosting environment for the application

---

### AWS S3 (File Storage)

* Stores uploaded images and generated thumbnails
* Files are saved with unique names using `UUID`
* Access is controlled (bucket is private by default)
* Designed to support scalable and durable file storage

---

### AWS RDS (Database)

* PostgreSQL database hosted on `AWS RDS`
* Stores application data:

  * users
  * image metadata (filename, URL, ownership)
* Enables centralized access for both local development and deployed application

---

### AWS EC2 (Application Hosting)

* The FastAPI application runs inside a `Docker` container on an EC2 instance
* Handles incoming API requests
* Connects to:

  * `AWS S3` for file storage
  * `AWS RDS` for database operations

---

### Integration Overview

* The application communicates with AWS services via:

  * `boto3` (for S3)
  * standard database drivers (for PostgreSQL)
* Configuration is managed via environment variables (`.env`)
* Credentials are not hardcoded and are injected securely at runtime

## License

This project is provided for `educational purposes` only.

It is intended to demonstrate backend development, cloud integration, and deployment practices using modern technologies such as `FastAPI`, `AWS`, and `Docker`.

You are free to use, modify, and learn from this code.
