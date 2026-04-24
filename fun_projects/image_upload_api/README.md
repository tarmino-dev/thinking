# Image Upload API

A cloud-based backend service for uploading, processing, and storing images using FastAPI and AWS.

## Overview

This project is a backend service that allows users to upload images, process them, and store them in a cloud environment.

The application is built with `FastAPI` and follows a modular architecture, separating API logic, business logic, and infrastructure components. Uploaded images are processed (resized and converted into thumbnails) and stored in `AWS S3`, while metadata is persisted in a `PostgreSQL` database hosted on `AWS RDS`.

The service includes user authentication using `JWT` and demonstrates a complete cloud-based workflow, including containerization with `Docker` and automated deployment using `GitHub Actions`.

This project is designed to showcase practical experience with backend development, cloud services, and deployment pipelines in a production-like environment.

## Features

* User registration and authentication using `JWT`
* Secure password storage with hashing (`bcrypt`)
* Image upload via REST API endpoint (`/upload`)
* Image processing:

  * Automatic resizing (max dimensions limit)
  * Thumbnail generation
* Cloud storage integration:

  * Images stored in `AWS S3`
  * Unique file naming using `UUID`
* Database integration:

  * Metadata stored in `PostgreSQL` (`AWS RDS`)
* Protected endpoints:

  * Upload requires valid authentication token
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

## Architecture

The application follows a modular and layered architecture, separating concerns between API, business logic, data access, and infrastructure configuration.

### Structure

* `app/api` — API layer (routes, request handling, dependencies)
* `app/services` — business logic (file storage, image processing)
* `app/db` — database layer (models, session, CRUD operations)
* `app/core` — configuration and security (settings, JWT, hashing)
* `app/schemas` — data validation and serialization (Pydantic models)

### Data Flow

1. A client sends a request to the API (e.g., `POST /upload`)
2. The request is validated using `Pydantic` schemas
3. Authentication is verified via `JWT`
4. The file is passed to the service layer
5. The service:

   * processes the image (`resize`, `thumbnail`)
   * uploads it to `AWS S3`
6. The API stores metadata (file URL, filename, user reference) in `PostgreSQL` (`AWS RDS`)
7. The response is returned to the client

## Architecture Diagram

```
                ┌───────────────┐
                │     Client    │
                │ (Browser/API) │
                └───────┬───────┘
                        │ HTTP Requests
                        ▼
              ┌───────────────────┐
              │    FastAPI App    │
              │(Docker on AWS EC2)│
              └─────────┬─────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   AWS S3      │               │   AWS RDS     │
│ (File Storage)│               │ (PostgreSQL)  │
└───────────────┘               └───────────────┘

```

### Flow Description

1. The `Client` sends HTTP requests to the `FastAPI` application (running in a Docker container on AWS EC2)
2. For image uploads:

   * The file is processed (resize + thumbnail)
   * The processed image is uploaded to `AWS S3`
3. Metadata (file URL, filename, user) is stored in `PostgreSQL` (`AWS RDS`)
4. The API returns responses back to the client

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

Response:

```json id="m4c1qx"
{
  "id": 1,
  "filename": "example.jpg"
}
```

---

#### `GET /images`

Retrieve a list of uploaded images.

Response:

```json id="k7t9fj"
[
  {
    "id": 1,
    "filename": "example.jpg",
    "path": "https://s3.amazonaws.com/..."
  }
]
```

---

#### `GET /images/{image_id}`

Retrieve a single image record by ID.

Response:

```json id="p3h6zn"
{
  "id": 1,
  "filename": "example.jpg",
  "path": "https://s3.amazonaws.com/..."
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

### 3. Run with Docker

```bash
docker-compose up --build
```

---

### 4. Access the API

Open your browser and navigate to:

```text
http://localhost:8000/docs
```

This will open the interactive Swagger UI where you can test all endpoints.

---

### Notes

* The application connects to a remote database (`AWS RDS`) by default
* For local development without AWS services:
  * set `STORAGE_TYPE=local`
  * optionally configure a local PostgreSQL instance and update `DATABASE_URL`
* If using `STORAGE_TYPE=s3`, make sure your AWS credentials are correctly configured

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
